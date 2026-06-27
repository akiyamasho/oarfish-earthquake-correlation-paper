# Oarfish Sightings and Global M7+ Earthquakes

**Paper PDF:** [output/pdf/oarfish_acm_paper.pdf](output/pdf/oarfish_acm_paper.pdf)

**Title:** Do Global M7+ Earthquakes Occur Disproportionately After Oarfish Sightings?

**Author:** Sho Akiyama, Independent Researcher

This repository contains an ACM-style empirical manuscript, rendered PDF, data outputs, figures, and reproducibility scripts for testing whether global `M7+` earthquakes occur disproportionately after oarfish sightings.

## Research Question

The paper now answers one direct question:

> After an oarfish sighting, what percentage of events are followed by a global `M7+` earthquake, and is that percentage higher than the overall global calendar baseline?

The primary endpoint remains global and prospective:

- oarfish event date: `t_i`
- earthquake catalog: USGS FDSN global `M7+`
- temporal direction: later earthquakes only
- primary window: `0--180` days
- spatial radius: none

Shorter windows are sensitivity checks: `0--1`, `0--7`, and `0--90` days.

## Headline Results

Using GBIF-indexed Regalecidae records from `1980-01-01` through `2026-06-27`, the analysis found:

| Window | Sightings | Hits | After oarfish | Overall calendar | Ratio | Permutation p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `0--1` days | 351 | 24 | 6.8% | 7.2% | 0.95 | 0.722 |
| `0--7` days | 351 | 93 | 26.5% | 25.8% | 1.03 | 0.509 |
| `0--90` days | 350 | 331 | 94.6% | 96.0% | 0.99 | 0.970 |
| `0--180` days | 343 | 343 | 100.0% | 100.0% | 1.00 | 1.000 |

The empirical result is negative: in this reproducible GBIF-USGS dataset, global `M7+` earthquakes are not disproportionately likely after oarfish sightings compared with the overall global calendar baseline.

## Repository Contents

- [Rendered PDF](output/pdf/oarfish_acm_paper.pdf)
- [ACM LaTeX source](output/pdf/oarfish_acm_paper.tex)
- [Figure-generation script](output/pdf/make_figures.py)
- [Empirical analysis script](analysis/build_m7_oarfish_analysis.py)
- [Raw data outputs](data/raw/)
- [Processed data outputs](data/processed/)
- [Generated table inputs](output/pdf/tables/)
- [Generated figures](output/pdf/figures/)
- [BibTeX references](output/pdf/references.bib)

## Reproduce

From the repository root:

```bash
python3 analysis/build_m7_oarfish_analysis.py
python3 output/pdf/make_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf output/pdf/oarfish_acm_paper.tex
```

Verification:

```bash
rg -n "0--30|30 day|30-day|\\\\pm 30|±30|0-30|30d" output/pdf/oarfish_acm_paper.tex output/pdf/make_figures.py
rg -n "undefined|Citation.*undefined|Reference.*undefined|Rerun to get cross|Error" output/pdf/oarfish_acm_paper.log
pdfinfo output/pdf/oarfish_acm_paper.pdf
```

The only expected `30 days` mention is the historical Orihara et al. local Japanese study context.
