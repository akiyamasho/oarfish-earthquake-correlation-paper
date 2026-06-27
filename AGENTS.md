# Agent Instructions

This repository contains an ACM-style research manuscript and rendered PDF about oarfish sighting claims and major earthquakes.

## Scope

- Keep the primary analysis framing as global sighting-to-earthquake matching with no spatial radius over a `0--180` day prospective window.
- Do not reintroduce `30` days as a manuscript endpoint. Mentions of `30 days` are only acceptable when describing the historical Orihara et al. local Japanese study.
- Treat local distance radii as secondary mechanism checks, not the main claim.
- Treat the paper as an evidence synthesis and reproducible test design, not as a completed audited global event-level reanalysis.

## Important Files

- `output/pdf/oarfish_acm_paper.tex`: ACM LaTeX manuscript.
- `output/pdf/references.bib`: bibliography.
- `output/pdf/oarfish_acm_paper.pdf`: committed rendered PDF.
- `output/pdf/make_figures.py`: source for generated figures.
- `output/pdf/figures/`: generated figure assets used by the TeX.

## Build and Verification

Run from the repository root:

```bash
python output/pdf/make_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf output/pdf/oarfish_acm_paper.tex
```

After editing, verify:

```bash
rg -n "0--30|30 day|30-day|\\\\pm 30|±30|0-30|30d" output/pdf/oarfish_acm_paper.tex output/pdf/make_figures.py
rg -n "undefined|Citation.*undefined|Reference.*undefined|Rerun to get cross|Error" output/pdf/oarfish_acm_paper.log
pdfinfo output/pdf/oarfish_acm_paper.pdf
```

Expected `30 day` hits should only be historical references to Orihara et al., not active analysis windows.

## Source Discipline

- Prefer official earthquake catalog sources for event claims, especially USGS FDSN.
- Mark news reports as lower-tier occurrence evidence unless corroborated by institutional records.
- Keep base-rate calculations clearly labeled as diagnostic approximations, not inferential p-values.
- Do not claim predictive validity without audited event construction, reporting-effort adjustment, and permutation null tests.
