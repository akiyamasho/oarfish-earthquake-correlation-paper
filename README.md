# Oarfish-Earthquake Correlation Paper

ACM-style research manuscript on public claims that oarfish sightings are followed by major earthquakes.

The paper is an evidence synthesis and reproducible test design, not a completed audited global event-level reanalysis. It focuses on the global form of the claim: a reported oarfish sighting anywhere in the world followed by a major earthquake anywhere in the world within a six-month prospective window.

Author: Sho Akiyama, Independent Researcher

## Artifacts

- [Rendered PDF](output/pdf/oarfish_acm_paper.pdf)
- [ACM LaTeX source](output/pdf/oarfish_acm_paper.tex)
- [BibTeX references](output/pdf/references.bib)
- [Figure-generation script](output/pdf/make_figures.py)
- [Figure assets](output/pdf/figures/)

## Summary

The manuscript separates a global public-warning claim from a local biological-precursor claim. The primary proposed global endpoint is:

- oarfish sighting date `t_i`
- earthquake anywhere on Earth
- prospective window `0--180` days
- magnitude thresholds `M >= 6`, `M >= 7`, and `M >= 8`
- no spatial radius for the primary global analysis

Shorter `0--1`, `0--7`, and `0--90` day windows are treated as sensitivity checks. Local `100`, `500`, and `1000` km radii are secondary mechanism checks, not the main global claim.

The main conclusion is that current public evidence does not support treating oarfish sightings as earthquake forecasts. Worldwide earthquake base rates make long-window global temporal matches common even under randomness: using a homogeneous Poisson approximation to USGS 1990--2021 public counts, a random date is followed within 180 days by at least one global `M6+` earthquake with probability about `1.000`, by at least one `M7+` with probability about `0.999`, and by at least one `M8+` with probability about `0.398`.

The paper includes a concrete example from a February 20, 2026 oarfish report near Cabo San Lucas, Mexico and June 2026 USGS `M6+` earthquakes in the Philippines, Japan, and Venezuela. These are real matches under a global `0--180` day rule, but the baseline calculation shows why this kind of match is not strong evidence by itself.

## Build

From the repository root:

```bash
python output/pdf/make_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf output/pdf/oarfish_acm_paper.tex
```

The final PDF was rendered with TeX Live 2026 and visually checked with Poppler page images.

## Repository Notes

- LaTeX build outputs are ignored.
- The final PDF is intentionally committed.
- Figure PDFs and PNGs are committed so the manuscript can be inspected without regenerating them.
