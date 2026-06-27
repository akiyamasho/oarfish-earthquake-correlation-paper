from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np


BASE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
SUMMARY_JSON = BASE / "data" / "processed" / "m7_analysis_summary.json"
SUMMARY_CSV = BASE / "data" / "processed" / "m7_analysis_summary.csv"

BLUE = "#1f77b4"
ORANGE = "#ff7f0e"
GREEN = "#2ca02c"
GRAY = "#6b7280"
LIGHT = "#f3f4f6"


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def load_summary():
    if not SUMMARY_JSON.exists() or not SUMMARY_CSV.exists():
        raise FileNotFoundError(
            "Run `python3 analysis/build_m7_oarfish_analysis.py` before making figures."
        )
    summary = json.loads(SUMMARY_JSON.read_text())
    with SUMMARY_CSV.open() as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for key in row:
            if key != "window":
                row[key] = float(row[key])
        row["window"] = int(row["window"])
    return summary, rows


def add_box(ax, xy, text, w=0.24, h=0.12, fc=LIGHT, ec=GRAY, fs=8):
    x, y = xy
    box = Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=1.1, zorder=2)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, zorder=3)
    return box


def add_arrow(ax, start, end, color=GRAY):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="->",
            mutation_scale=12,
            linewidth=1.2,
            color=color,
            zorder=1,
        )
    )


def global_linkage_schematic(summary):
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.set_xlim(0, 180)
    ax.set_ylim(-0.9, 2.2)
    ax.axis("off")

    ax.add_patch(Rectangle((0, -0.11), 180, 0.22, facecolor="#fef3c7", edgecolor="none"))
    ax.hlines(0, 0, 180, color="#111827", linewidth=2.2)
    for x in [0, 1, 7, 90, 180]:
        ax.vlines(x, -0.13, 0.13, color="#111827", linewidth=1)
        ax.text(x, -0.34, f"{x}d", ha="center", fontsize=8)
    ax.scatter([0], [0], s=180, marker="*", color=ORANGE, zorder=4)
    ax.text(0, 0.42, "oarfish\nsighting", ha="center", fontsize=9)
    ax.scatter([36, 114, 161], [0.78, 1.2, 0.68], s=65, color=BLUE, edgecolor="white", zorder=5)
    for x, y in [(36, 0.78), (114, 1.2), (161, 0.68)]:
        ax.text(x, y + 0.19, "eligible\nglobal M7+", ha="center", fontsize=8)
    ax.text(
        90,
        1.9,
        "Global M7+ post-sighting test: no spatial radius, 0-180 day primary window",
        ha="center",
        fontsize=12,
        weight="bold",
    )
    ax.text(
        90,
        -0.67,
        f"{summary['accepted_oarfish_events']} accepted GBIF Regalecidae events are compared with "
        f"{summary['usgs_m7plus_events']} USGS M7+ earthquakes.",
        ha="center",
        fontsize=8,
    )
    save(fig, "global_linkage_schematic")


def pipeline_diagram():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    boxes = [
        ((0.04, 0.66), "GBIF\nRegalecidae\nrecords"),
        ((0.31, 0.66), "Day-dated\nrecords and\ndeduplication"),
        ((0.58, 0.66), "Accepted\noarfish\nevents"),
        ((0.04, 0.25), "USGS global\nM7+\nearthquakes"),
        ((0.31, 0.25), "Post-sighting\nlinkage by\nwindow"),
        ((0.58, 0.25), "Calendar and\npermutation\nbaselines"),
    ]
    for xy, text in boxes:
        add_box(ax, xy, text, w=0.22, h=0.18, fs=8)
    add_box(ax, (0.80, 0.45), "Observed vs.\noverall\npercentages", w=0.16, h=0.18, fc="#e0f2fe")

    for a, b in [
        ((0.26, 0.75), (0.31, 0.75)),
        ((0.53, 0.75), (0.58, 0.75)),
        ((0.69, 0.66), (0.80, 0.55)),
        ((0.26, 0.34), (0.31, 0.34)),
        ((0.53, 0.34), (0.58, 0.34)),
        ((0.69, 0.43), (0.80, 0.52)),
        ((0.15, 0.66), (0.39, 0.43)),
        ((0.15, 0.43), (0.39, 0.34)),
    ]:
        add_arrow(ax, a, b)
    ax.text(0.5, 0.93, "Implemented global M7+ analysis pipeline", ha="center", fontsize=13, weight="bold")
    save(fig, "pipeline_diagram")


def null_model_schematic():
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    add_box(ax, (0.05, 0.62), "Observed\noarfish dates", w=0.18, h=0.16, fc="#fff7ed")
    add_box(ax, (0.32, 0.62), "Observed\nM7+ hit\npercentage", w=0.18, h=0.16, fc="#e0f2fe")
    add_box(ax, (0.05, 0.24), "Same-year\ncontrol dates", w=0.18, h=0.16)
    add_box(ax, (0.32, 0.24), "Null hit\npercentages", w=0.18, h=0.16)
    add_box(ax, (0.68, 0.43), "Upper-tail p:\n(1 + null >= observed)\n/ (B + 1)", w=0.25, h=0.18, fc="#ecfdf5")
    for a, b in [
        ((0.23, 0.70), (0.32, 0.70)),
        ((0.23, 0.32), (0.32, 0.32)),
        ((0.50, 0.70), (0.68, 0.55)),
        ((0.50, 0.32), (0.68, 0.49)),
        ((0.14, 0.62), (0.14, 0.40)),
    ]:
        add_arrow(ax, a, b)
    ax.text(0.14, 0.52, "randomize within\ncalendar year", ha="center", fontsize=8)
    ax.text(0.5, 0.91, "Calendar-matched null model", ha="center", fontsize=13, weight="bold")
    save(fig, "null_model_schematic")


def observed_vs_overall(rows):
    windows = [row["window"] for row in rows]
    observed = np.array([row["observed_pct"] * 100 for row in rows])
    baseline = np.array([row["baseline_pct"] * 100 for row in rows])
    x = np.arange(len(windows))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.bar(x - width / 2, observed, width, label="After oarfish sightings", color=ORANGE)
    ax.bar(x + width / 2, baseline, width, label="Overall calendar dates", color=BLUE)
    ax.set_xticks(x)
    ax.set_xticklabels([f"0-{w}d" for w in windows])
    ax.set_ylim(0, 108)
    ax.set_ylabel("Dates/events followed by global M7+ (%)")
    ax.set_xlabel("Prospective window")
    ax.set_title("Observed post-oarfish percentages vs. overall global baseline", fontsize=12, weight="bold")
    ax.legend(frameon=False, loc="upper left")
    for xpos, value in zip(x - width / 2, observed):
        ax.text(xpos, value + 2, f"{value:.1f}", ha="center", fontsize=8)
    for xpos, value in zip(x + width / 2, baseline):
        ax.text(xpos, value + 2, f"{value:.1f}", ha="center", fontsize=8)
    save(fig, "m7_observed_vs_overall")


def permutation_histogram(rows):
    row = next(item for item in rows if item["window"] == 7)
    path = BASE / "data" / "processed" / "permutation_null_7d.csv"
    with path.open() as fh:
        values = [int(row["hit_count"]) for row in csv.DictReader(fh)]
    fig, ax = plt.subplots(figsize=(7.0, 3.7))
    ax.hist(values, bins=range(min(values), max(values) + 2), color="#bfdbfe", edgecolor="#1e3a8a")
    ax.axvline(row["observed_hits"], color=ORANGE, linewidth=2.4, label=f"observed = {int(row['observed_hits'])}")
    ax.axvline(row["perm_mean"], color=GREEN, linewidth=2.0, linestyle="--", label=f"null mean = {row['perm_mean']:.1f}")
    ax.set_title("Seven-day M7+ sensitivity check against same-year null", fontsize=12, weight="bold")
    ax.set_xlabel("Oarfish events followed by at least one global M7+ earthquake")
    ax.set_ylabel("Permutation replicates")
    ax.legend(frameon=False)
    save(fig, "permutation_null_7d")


def bias_dag():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    nodes = {
        "Oceanography": (0.08, 0.66),
        "Fishing /\nbeach access": (0.08, 0.28),
        "Media /\ncitizen science": (0.36, 0.28),
        "Indexed\noarfish event": (0.36, 0.66),
        "Earthquake\noccurrence": (0.70, 0.66),
        "Observed\nassociation": (0.70, 0.28),
    }
    for text, (x, y) in nodes.items():
        add_box(ax, (x, y), text, w=0.20, h=0.14, fc="#f8fafc")
    centers = {key: (value[0] + 0.10, value[1] + 0.07) for key, value in nodes.items()}
    for a, b in [
        ("Oceanography", "Indexed\noarfish event"),
        ("Fishing /\nbeach access", "Indexed\noarfish event"),
        ("Media /\ncitizen science", "Indexed\noarfish event"),
        ("Media /\ncitizen science", "Observed\nassociation"),
        ("Indexed\noarfish event", "Observed\nassociation"),
        ("Earthquake\noccurrence", "Observed\nassociation"),
    ]:
        add_arrow(ax, centers[a], centers[b])
    ax.text(0.5, 0.92, "Observation and reporting pathways", ha="center", fontsize=13, weight="bold")
    save(fig, "bias_dag")


if __name__ == "__main__":
    summary, rows = load_summary()
    global_linkage_schematic(summary)
    pipeline_diagram()
    null_model_schematic()
    observed_vs_overall(rows)
    permutation_histogram(rows)
    bias_dag()
