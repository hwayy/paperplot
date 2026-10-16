<!-- Generated from docs/api.md by tools/build_skill.py. Do not edit directly. -->

# API Reference

Import the public API from `paperplot`.

## Example

LaTeX rendering is enabled by default and requires `latex` on `PATH`, with the
`amsmath` and `bm` packages. PNG rendering also requires `dvipng`. For tests, CI
without LaTeX, or temporary diagnostics, pass `usetex=False` to `style_context`.

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

This writes `results/figures/example.pdf`.

## Presets and Layout

| Preset | Target |
| --- | --- |
| `manuscript_single` | One-column paper figure. |
| `manuscript_double` | Two-column paper figure or wide panel. |
| `slides_single` | One large slide figure. |
| `slides_double` | Wide slide figure. |
| `slides_grid` | Multi-panel slide figure. |
| `compact_panel` | Small diagnostic or inset-like panel. |

`PlotSpec` is an immutable dataclass holding figure geometry and style settings.
Pass overrides to `get_preset` or `style_context`:

| Fields | Meaning |
| --- | --- |
| `plot_width_cm`, `plot_height_cm` | Figure dimensions; height is computed from the layout when omitted. |
| `margin_left_cm`, `margin_right_cm`, `margin_bottom_cm`, `margin_top_cm` | Outer margins. |
| `space_width_cm`, `space_height_cm` | Gaps between panels. |
| `subplot_ratio` | Panel height divided by panel width. |
| `font_size`, `dpi` | Font size in points and raster resolution. |
| `latex_preamble` | LaTeX packages and commands; defaults to `amsmath` and `bm`. |

Useful computed properties are `subplot_width_cm`, `subplot_height_cm`,
`height_cm`, `figsize_inches`, and `subplot_adjust`.

## Functions

### `get_preset(name="manuscript_single", *, nrows=1, ncols=1, **overrides)`

Return a `PlotSpec` for a named preset. Row and column counts must be positive;
an unknown preset raises `KeyError`.

### `style_context(preset="manuscript_single", *, nrows=1, ncols=1, usetex=True, **overrides)`

Apply Matplotlib settings inside a `with` block and yield the active `PlotSpec`.
Settings are restored on exit. Missing `latex` raises `RuntimeError` when
`usetex=True`.

### `subplots(nrows=1, ncols=1, *, preset="manuscript_single", spec=None, usetex=True, **kwargs)`

Return `(fig, axes)` with figure dimensions and subplot spacing applied. Pass
the context's `spec` to reuse its overrides; use the same row and column counts
in both calls. Extra keywords, such as `sharex=True`, go to
`matplotlib.pyplot.subplots`. Use `style_context` to apply text and style settings.

### `apply_axes_style(ax, *, grid=True, legend_fontsize=None)`

Style ticks, the grid, and an existing legend. Call after creating the legend;
`legend_fontsize` optionally overrides its text size.

### `savefig(fig, path, *, formats=None, dpi=None)`

Create parent directories and return a list of written `Path` objects. The
default format is PDF. Use `formats="png"` or `formats=("pdf", "png")` for other
exports. Any path suffix is replaced with the selected format; a `.png` suffix
alone does not select PNG. `dpi=None` uses Matplotlib's configured export DPI.
