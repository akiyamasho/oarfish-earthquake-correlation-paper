#!/usr/bin/env python3
from __future__ import annotations

import bisect
import csv
import json
import math
import random
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "output" / "pdf" / "tables"
for path in (RAW, PROCESSED, TABLES):
    path.mkdir(parents=True, exist_ok=True)

START = date(1980, 1, 1)
END = date(2026, 6, 27)
WINDOWS = (1, 7, 90, 180)
GBIF_TAXON_KEY = 3715
GBIF_LIMIT = 300
PERMUTATIONS = 10000
RANDOM_SEED = 20260627


@dataclass
class OarfishRecord:
    gbif_id: str
    event_date: date
    lat: float | None
    lon: float | None
    country: str
    locality: str
    basis: str
    scientific_name: str
    dataset_name: str
    references: str
    occurrence_id: str
    has_media: bool


@dataclass
class OarfishEvent:
    event_id: str
    event_date: date
    lat: float | None
    lon: float | None
    country: str
    locality: str
    basis: str
    scientific_name: str
    source_records: list[str]
    dataset_names: list[str]
    references: list[str]
    has_media: bool


@dataclass
class Earthquake:
    earthquake_id: str
    origin_time: datetime
    event_date: date
    lat: float
    lon: float
    depth_km: float
    mag: float
    mag_type: str
    place: str
    status: str
    url: str


def fetch_json(url: str) -> dict:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "oarfish-m7-analysis/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "oarfish-m7-analysis/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read().decode("utf-8")


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    token = value[:10]
    try:
        return date.fromisoformat(token)
    except ValueError:
        return None


def parse_usgs_time(value: str) -> datetime:
    cleaned = value.replace("Z", "+00:00")
    if "." in cleaned:
        head, tail = cleaned.split(".", 1)
        zone = ""
        if "+" in tail:
            fraction, zone = tail.split("+", 1)
            zone = "+" + zone
        elif "-" in tail:
            fraction, zone = tail.rsplit("-", 1)
            zone = "-" + zone
        else:
            fraction = tail
        cleaned = f"{head}.{fraction[:6]}{zone}"
    return datetime.fromisoformat(cleaned).astimezone(timezone.utc)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split())


def fetch_gbif_records() -> list[OarfishRecord]:
    params = {
        "taxon_key": str(GBIF_TAXON_KEY),
        "eventDate": f"{START.isoformat()},{END.isoformat()}",
        "limit": str(GBIF_LIMIT),
        "offset": "0",
    }
    records: list[OarfishRecord] = []
    while True:
        url = "https://api.gbif.org/v1/occurrence/search?" + urllib.parse.urlencode(params)
        payload = fetch_json(url)
        for row in payload.get("results", []):
            event_date = parse_date(row.get("eventDate"))
            if event_date is None:
                continue
            if row.get("occurrenceStatus") and row.get("occurrenceStatus") != "PRESENT":
                continue
            lat = row.get("decimalLatitude")
            lon = row.get("decimalLongitude")
            media = row.get("media") or []
            records.append(
                OarfishRecord(
                    gbif_id=str(row.get("key") or row.get("gbifID") or ""),
                    event_date=event_date,
                    lat=float(lat) if lat is not None else None,
                    lon=float(lon) if lon is not None else None,
                    country=clean_text(row.get("country") or row.get("countryCode")),
                    locality=clean_text(row.get("verbatimLocality") or row.get("locality")),
                    basis=clean_text(row.get("basisOfRecord")),
                    scientific_name=clean_text(row.get("acceptedScientificName") or row.get("scientificName")),
                    dataset_name=clean_text(row.get("datasetName")),
                    references=clean_text(row.get("references")),
                    occurrence_id=clean_text(row.get("occurrenceID")),
                    has_media=bool(media),
                )
            )
        if payload.get("endOfRecords") or not payload.get("results"):
            break
        params["offset"] = str(int(params["offset"]) + GBIF_LIMIT)
    return records


def write_raw_gbif(records: list[OarfishRecord]) -> None:
    with (RAW / "gbif_regalecidae_1980_2026.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            lineterminator="\n",
            fieldnames=[
                "gbif_id",
                "event_date",
                "lat",
                "lon",
                "country",
                "locality",
                "basis",
                "scientific_name",
                "dataset_name",
                "references",
                "occurrence_id",
                "has_media",
            ],
        )
        writer.writeheader()
        for row in records:
            writer.writerow(
                {
                    "gbif_id": row.gbif_id,
                    "event_date": row.event_date.isoformat(),
                    "lat": "" if row.lat is None else row.lat,
                    "lon": "" if row.lon is None else row.lon,
                    "country": row.country,
                    "locality": row.locality,
                    "basis": row.basis,
                    "scientific_name": row.scientific_name,
                    "dataset_name": row.dataset_name,
                    "references": row.references,
                    "occurrence_id": row.occurrence_id,
                    "has_media": int(row.has_media),
                }
            )


def duplicate_match(record: OarfishRecord, event: OarfishEvent) -> bool:
    if abs((record.event_date - event.event_date).days) > 3:
        return False
    if record.lat is not None and record.lon is not None and event.lat is not None and event.lon is not None:
        return haversine_km(record.lat, record.lon, event.lat, event.lon) <= 10
    if record.event_date != event.event_date:
        return False
    locality = record.locality.lower()[:60]
    event_locality = event.locality.lower()[:60]
    return bool(record.country and record.country == event.country and locality and locality == event_locality)


def deduplicate(records: list[OarfishRecord]) -> list[OarfishEvent]:
    events: list[OarfishEvent] = []
    for record in sorted(records, key=lambda r: (r.event_date, r.country, r.locality, r.gbif_id)):
        matched = None
        for event in reversed(events):
            if (record.event_date - event.event_date).days > 3:
                break
            if duplicate_match(record, event):
                matched = event
                break
        if matched is None:
            matched = OarfishEvent(
                event_id=f"OF{len(events) + 1:04d}",
                event_date=record.event_date,
                lat=record.lat,
                lon=record.lon,
                country=record.country,
                locality=record.locality,
                basis=record.basis,
                scientific_name=record.scientific_name,
                source_records=[],
                dataset_names=[],
                references=[],
                has_media=False,
            )
            events.append(matched)
        matched.source_records.append(record.gbif_id)
        if record.dataset_name and record.dataset_name not in matched.dataset_names:
            matched.dataset_names.append(record.dataset_name)
        if record.references and record.references not in matched.references:
            matched.references.append(record.references)
        matched.has_media = matched.has_media or record.has_media
        if matched.lat is None and record.lat is not None:
            matched.lat = record.lat
            matched.lon = record.lon
    return events


def write_events(events: list[OarfishEvent]) -> None:
    with (PROCESSED / "oarfish_events.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            lineterminator="\n",
            fieldnames=[
                "event_id",
                "event_date",
                "lat",
                "lon",
                "country",
                "locality",
                "basis",
                "scientific_name",
                "source_record_count",
                "source_record_ids",
                "dataset_names",
                "references",
                "has_media",
            ],
        )
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    "event_id": event.event_id,
                    "event_date": event.event_date.isoformat(),
                    "lat": "" if event.lat is None else event.lat,
                    "lon": "" if event.lon is None else event.lon,
                    "country": event.country,
                    "locality": event.locality,
                    "basis": event.basis,
                    "scientific_name": event.scientific_name,
                    "source_record_count": len(event.source_records),
                    "source_record_ids": ";".join(event.source_records),
                    "dataset_names": ";".join(event.dataset_names),
                    "references": ";".join(event.references),
                    "has_media": int(event.has_media),
                }
            )


def fetch_usgs_m7() -> list[Earthquake]:
    params = {
        "format": "csv",
        "starttime": START.isoformat(),
        "endtime": f"{END.isoformat()}T23:59:59",
        "minmagnitude": "7",
        "orderby": "time-asc",
    }
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urllib.parse.urlencode(params)
    text = fetch_text(url)
    (RAW / "usgs_m7plus_1980_2026.csv").write_text(text.replace("\r\n", "\n"))
    rows = csv.DictReader(text.splitlines())
    quakes: list[Earthquake] = []
    for row in rows:
        origin = parse_usgs_time(row["time"])
        quakes.append(
            Earthquake(
                earthquake_id=row["id"],
                origin_time=origin,
                event_date=origin.date(),
                lat=float(row["latitude"]),
                lon=float(row["longitude"]),
                depth_km=float(row["depth"]),
                mag=float(row["mag"]),
                mag_type=row["magType"],
                place=row["place"],
                status=row["status"],
                url=f"https://earthquake.usgs.gov/earthquakes/eventpage/{row['id']}",
            )
        )
    return quakes


def has_quake_after(start_date: date, window: int, quake_ordinals: list[int]) -> bool:
    start_ord = start_date.toordinal()
    idx = bisect.bisect_left(quake_ordinals, start_ord)
    return idx < len(quake_ordinals) and quake_ordinals[idx] <= start_ord + window


def first_quake_after(start_date: date, window: int, quakes: list[Earthquake]) -> Earthquake | None:
    quake_ordinals = [q.event_date.toordinal() for q in quakes]
    idx = bisect.bisect_left(quake_ordinals, start_date.toordinal())
    if idx < len(quakes) and quake_ordinals[idx] <= start_date.toordinal() + window:
        return quakes[idx]
    return None


def eligible_end(window: int) -> date:
    return END - timedelta(days=window)


def calendar_baseline(window: int, quake_ordinals: list[int]) -> tuple[int, int]:
    end = eligible_end(window)
    hit = 0
    total = 0
    current = START
    while current <= end:
        total += 1
        if has_quake_after(current, window, quake_ordinals):
            hit += 1
        current += timedelta(days=1)
    return hit, total


def binomial_upper_tail(k: int, n: int, p: float) -> float:
    if k <= 0:
        return 1.0
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0 if k <= n else 0.0
    logs = []
    logp = math.log(p)
    logq = math.log1p(-p)
    for x in range(k, n + 1):
        logs.append(math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1) + x * logp + (n - x) * logq)
    max_log = max(logs)
    return min(1.0, math.exp(max_log) * sum(math.exp(value - max_log) for value in logs))


def year_candidate_dates(window: int) -> dict[int, list[date]]:
    end = eligible_end(window)
    candidates: dict[int, list[date]] = defaultdict(list)
    current = START
    while current <= end:
        candidates[current.year].append(current)
        current += timedelta(days=1)
    return candidates


def permutation_p(
    events: list[OarfishEvent],
    window: int,
    observed_hits: int,
    quake_ordinals: list[int],
    rng: random.Random,
) -> tuple[float, float, float, float]:
    candidates = year_candidate_dates(window)
    eligible_events = [event for event in events if event.event_date <= eligible_end(window)]
    global_pool = [day for days in candidates.values() for day in days]
    null_hits: list[int] = []
    for _ in range(PERMUTATIONS):
        hits = 0
        for event in eligible_events:
            pool = candidates.get(event.event_date.year) or global_pool
            control_date = rng.choice(pool)
            hits += int(has_quake_after(control_date, window, quake_ordinals))
        null_hits.append(hits)
    null_hits.sort()
    ge = sum(1 for value in null_hits if value >= observed_hits)
    p_value = (1 + ge) / (PERMUTATIONS + 1)
    mean = sum(null_hits) / len(null_hits)
    lo = null_hits[int(0.025 * len(null_hits))]
    hi = null_hits[int(0.975 * len(null_hits))]
    with (PROCESSED / f"permutation_null_{window}d.csv").open("w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["replicate", "hit_count"])
        for idx, value in enumerate(null_hits, start=1):
            writer.writerow([idx, value])
    return p_value, mean, lo, hi


def write_linkages(events: list[OarfishEvent], quakes: list[Earthquake]) -> None:
    with (PROCESSED / "global_m7_linkages.csv").open("w", newline="") as fh:
        fields = ["event_id", "event_date", "eligible_180d", "first_m7plus_id", "first_m7plus_date", "days_after_sighting"]
        fields.extend([f"within_{w}d" for w in WINDOWS])
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for event in events:
            first = first_quake_after(event.event_date, 180, quakes)
            row = {
                "event_id": event.event_id,
                "event_date": event.event_date.isoformat(),
                "eligible_180d": int(event.event_date <= eligible_end(180)),
                "first_m7plus_id": first.earthquake_id if first else "",
                "first_m7plus_date": first.event_date.isoformat() if first else "",
                "days_after_sighting": "" if first is None else (first.event_date - event.event_date).days,
            }
            quake_ordinals = [q.event_date.toordinal() for q in quakes]
            for window in WINDOWS:
                row[f"within_{window}d"] = (
                    "" if event.event_date > eligible_end(window) else int(has_quake_after(event.event_date, window, quake_ordinals))
                )
            writer.writerow(row)


def pct(value: float) -> str:
    return f"{100 * value:.1f}\\%"


def format_p(value: float) -> str:
    if value < 0.001:
        return "$<0.001$"
    return f"{value:.3f}"


def write_tex_table(rows: list[dict]) -> None:
    lines = [
        "\\small",
        "\\begin{tabular}{@{}lrrrrrr@{}}",
        "\\toprule",
        "Window & Sightings & Hits & Observed & Overall & Ratio & Perm. $p$ \\\\",
        "\\midrule",
    ]
    for row in rows:
        ratio = "--" if row["baseline_pct"] == 0 else f"{row['observed_pct'] / row['baseline_pct']:.2f}"
        lines.append(
            f"0--{row['window']} days & {row['eligible_sightings']} & {row['observed_hits']} & "
            f"{pct(row['observed_pct'])} & {pct(row['baseline_pct'])} & {ratio} & {format_p(row['perm_p'])} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    (TABLES / "m7_empirical_results.tex").write_text("\n".join(lines) + "\n")


def main() -> int:
    rng = random.Random(RANDOM_SEED)
    records = fetch_gbif_records()
    write_raw_gbif(records)
    events = deduplicate(records)
    write_events(events)
    quakes = fetch_usgs_m7()
    write_linkages(events, quakes)
    quake_ordinals = [quake.event_date.toordinal() for quake in quakes]

    basis_counts = Counter(record.basis for record in records)
    event_basis_counts = Counter(event.basis for event in events)
    rows = []
    for window in WINDOWS:
        eligible_events = [event for event in events if event.event_date <= eligible_end(window)]
        observed_hits = sum(has_quake_after(event.event_date, window, quake_ordinals) for event in eligible_events)
        calendar_hits, calendar_total = calendar_baseline(window, quake_ordinals)
        baseline_pct = calendar_hits / calendar_total
        observed_pct = observed_hits / len(eligible_events) if eligible_events else 0
        binom_p = binomial_upper_tail(observed_hits, len(eligible_events), baseline_pct)
        perm_p, perm_mean, perm_lo, perm_hi = permutation_p(events, window, observed_hits, quake_ordinals, rng)
        rows.append(
            {
                "window": window,
                "eligible_sightings": len(eligible_events),
                "observed_hits": observed_hits,
                "observed_pct": observed_pct,
                "calendar_hit_days": calendar_hits,
                "calendar_total_days": calendar_total,
                "baseline_pct": baseline_pct,
                "expected_hits": len(eligible_events) * baseline_pct,
                "binomial_p": binom_p,
                "perm_p": perm_p,
                "perm_mean": perm_mean,
                "perm_lo": perm_lo,
                "perm_hi": perm_hi,
            }
        )

    summary = {
        "study_start": START.isoformat(),
        "study_end": END.isoformat(),
        "gbif_taxon_key": GBIF_TAXON_KEY,
        "raw_gbif_records": len(records),
        "accepted_oarfish_events": len(events),
        "basis_counts_raw": dict(basis_counts),
        "basis_counts_events": dict(event_basis_counts),
        "usgs_m7plus_events": len(quakes),
        "windows": rows,
        "permutations": PERMUTATIONS,
        "random_seed": RANDOM_SEED,
    }
    (PROCESSED / "m7_analysis_summary.json").write_text(json.dumps(summary, indent=2))
    with (PROCESSED / "m7_analysis_summary.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_tex_table(rows)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
