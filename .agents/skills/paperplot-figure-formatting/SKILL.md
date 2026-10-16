---
name: paperplot-figure-formatting
description: Use this skill whenever creating, editing, reviewing, or regenerating Matplotlib figures for papers, slides, reports, experiments, or result artifacts. It ensures figures use the standalone paperplot package for LaTeX-ready text, readable sizing, stable layout, PDF-first export, and overlap checks.
---

# Paperplot Figure Formatting

Use this skill whenever a task creates or modifies Matplotlib plotting code or regenerates Matplotlib figure artifacts.

## Workflow

1. Use `paperplot` as the default formatting layer:
   - `style_context(...)` for local Matplotlib rcParams.
   - `subplots(...)` for figure size and subplot spacing.
   - `apply_axes_style(...)` for axes, ticks, grid, and legend frame styling.
   - `savefig(...)` for exports.
2. Save canonical figures as PDF by default. Add PNG only when slides, web previews, or existing downstream tooling explicitly need raster copies.
3. Choose presets by target:
   - `manuscript_single` or `manuscript_double` for papers and reports.
   - `slides_single`, `slides_double`, or `slides_grid` for Beamer or slide figures.
   - `compact_panel` for small diagnostics.
4. Keep LaTeX rendering enabled for canonical results. Use `usetex=False` only for tests, CI environments without LaTeX, or temporary diagnostics.
5. Prefer layout overrides over ad hoc `plt.rcParams`, tiny font-size constants, or script-local style dictionaries.
6. Place shared legends outside axes when legends would obscure data. Remove redundant labels in dense grids if they cause overlap.
7. Render-check updated figures or the deck/manuscript pages that include them before finishing.
8. When the host repository has a research log, changelog, or result manifest convention, update it if regenerated figures or presentation/manuscript artifacts change the visible project state.

## Package Reference

The package repository is `https://github.com/Chiahwa/paperplot`. Use `paperplot`
from the active Python environment; no particular local checkout is required.

## API Reference

The core API is documented here so this skill can be installed independently of
the package repository.

- `get_preset(name="manuscript_single", *, nrows=1, ncols=1, **overrides)`
  returns an immutable `PlotSpec` with figure geometry and style settings.
- `style_context(preset="manuscript_single", *, nrows=1, ncols=1, usetex=True, **overrides)`
  applies settings inside a `with` block and yields the active `PlotSpec`.
  LaTeX rendering requires a working `latex` executable on `PATH`.
- `subplots(nrows=1, ncols=1, *, preset="manuscript_single", spec=None, usetex=True, **kwargs)`
  returns `(fig, axes)` with figure size and subplot spacing applied. Pass the
  context's `spec` to reuse its overrides, and use matching row/column counts.
  Extra keyword arguments go to `matplotlib.pyplot.subplots`, such as `sharex=True`.
- `apply_axes_style(ax, *, grid=True, legend_fontsize=None)` styles ticks, the
  grid, and an existing legend. Call it after creating the legend.
- `savefig(fig, path, *, formats=None, dpi=None)` creates parent directories,
  exports PDF by default, and returns a list of written `Path` objects. Use
  `formats="png"` or `formats=("pdf", "png")` for explicit output formats.

Layout overrides use centimeters: `plot_width_cm`, `plot_height_cm`,
`margin_left_cm`, `margin_right_cm`, `margin_bottom_cm`, `margin_top_cm`,
`space_width_cm`, and `space_height_cm`. `subplot_ratio` is panel height divided
by panel width. Figure height is computed from the layout unless
`plot_height_cm` is supplied. `font_size` uses points; `dpi` controls raster
resolution. `latex_preamble` customizes LaTeX packages and commands.

Minimal example (requires LaTeX):

```python
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from paperplot import apply_axes_style, savefig, style_context, subplots

with style_context("manuscript_single") as spec:
    fig, ax = subplots(spec=spec)
    ax.plot([0, 1, 2], [0, 1, 4], label=r"$y=x^2$")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend()
    apply_axes_style(ax)
    savefig(fig, "results/figures/example")
    plt.close(fig)
```
