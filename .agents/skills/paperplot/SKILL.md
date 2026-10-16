---
name: paperplot
description: Use this skill whenever creating, editing, reviewing, or regenerating Matplotlib figures for papers, slides, reports, experiments, or result artifacts. It ensures figures use the standalone paperplot package for LaTeX-ready text, readable sizing, stable layout, PDF-first export, and overlap checks.
---

# Paperplot

Use `paperplot` from the active Python environment. Before writing or changing
plotting code, read the bundled [API reference](references/api.md) for presets,
layout overrides, signatures, and an example. The reference ships with this
skill; no source checkout is required.

## Workflow

1. Use `style_context`, `subplots`, `apply_axes_style`, and `savefig` as the
   formatting layer. Choose a preset for the final target and prefer layout
   overrides over script-local style dictionaries or ad hoc `plt.rcParams`.
2. Save canonical figures as PDF. Add PNG when slides, web previews, or
   downstream tooling need raster copies.
3. Keep LaTeX enabled for canonical results. Use `usetex=False` only for tests,
   CI without LaTeX, or temporary diagnostics.
4. Place shared legends outside axes when they obscure data. Remove redundant
   labels in dense grids when they cause overlap; keep text readable.
5. Render-check updated figures or the manuscript/slide pages containing them
   for overlapping or clipped titles, labels, legends, and colorbars.
6. Follow the host repository's research log, changelog, or result manifest
   convention when regenerated artifacts change the visible project state.
