# Oarfish Earthquake Correlation Research

ACM-style research manuscript on oarfish sighting claims and major-earthquake correlation.

The paper is an evidence synthesis and reproducible test design, not a completed audited global event-level reanalysis. It uses the supplied research synthesis, public earthquake and biodiversity data-source documentation, and two rounds of independent research-panel review.

## Artifacts

- `output/pdf/oarfish_acm_paper.tex` - ACM-style LaTeX manuscript.
- `output/pdf/references.bib` - BibTeX references.
- `output/pdf/oarfish_acm_paper.pdf` - rendered final PDF.
- `output/pdf/figures/` - figure assets used by the manuscript.

## Build

From the manuscript directory:

```bash
cd output/pdf
latexmk -pdf -interaction=nonstopmode -halt-on-error oarfish_acm_paper.tex
```

The PDF was rendered and visually checked with Poppler page images.

## Main Conclusion

Current public evidence does not support treating oarfish sightings as earthquake forecasts. Global no-distance temporal matching is especially weak because worldwide `M6+` earthquake base rates make coincidences common even under randomness. A defensible 1980-2026 study requires audited Regalecidae event construction, official earthquake catalogs, explicit global and local endpoints, source reliability tiers, reporting-effort adjustment, and permutation null models.
