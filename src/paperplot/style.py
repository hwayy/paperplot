"""Matplotlib style presets for LaTeX-ready research figures.

The presets use centimeter units because manuscript and slide figure sizes are
usually chosen from document geometry rather than screen pixels.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

import matplotlib.pyplot as plt
from cycler import cycler

CM_PER_INCH = 2.54
DEFAULT_LATEX_PREAMBLE = r"\usepackage{amsmath}\usepackage{bm}"
DEFAULT_FORMATS = ("pdf",)
_FIXED_LAYOUT_PARAMS = {
    "figure.autolayout": False,
    "figure.constrained_layout.use": False,
}


@dataclass(frozen=True)
class PlotSpec:
    """Complete figure style and layout specification.

    Dimensions are stored in centimeters. ``plot_height_cm`` is optional; when
    omitted it is derived from the number of rows, columns, subplot aspect
    ratio, margins, and inter-panel spacing.
    """

    name: str
    plot_width_cm: float
    margin_left_cm: float
    margin_right_cm: float
    margin_bottom_cm: float
    margin_top_cm: float
    space_width_cm: float
    space_height_cm: float
    subplot_ratio: float
    font_size: float
    nrows: int = 1
    ncols: int = 1
    plot_height_cm: float | None = None
    dpi: int = 300
    usetex: bool = True
    latex_preamble: str = DEFAULT_LATEX_PREAMBLE
    default_formats: tuple[str, ...] = DEFAULT_FORMATS

    @property
    def subplot_width_cm(self) -> float:
        width = (
            self.plot_width_cm
            - self.margin_left_cm
            - self.margin_right_cm
            - (self.ncols - 1) * self.space_width_cm
        ) / self.ncols
        if width <= 0:
            raise ValueError("computed subplot width must be positive")
        return width

    @property
    def subplot_height_cm(self) -> float:
        if self.plot_height_cm is None:
            height = self.subplot_width_cm * self.subplot_ratio
        else:
            height = (
                self.plot_height_cm
                - self.margin_bottom_cm
                - self.margin_top_cm
                - (self.nrows - 1) * self.space_height_cm
            ) / self.nrows
        if height <= 0:
            raise ValueError("computed subplot height must be positive")
        return height

    @property
    def height_cm(self) -> float:
        if self.plot_height_cm is not None:
            return self.plot_height_cm
        return (
            self.nrows * self.subplot_height_cm
            + self.margin_bottom_cm
            + self.margin_top_cm
            + (self.nrows - 1) * self.space_height_cm
        )

    @property
    def figsize_inches(self) -> tuple[float, float]:
        return (self.plot_width_cm / CM_PER_INCH, self.height_cm / CM_PER_INCH)

    @property
    def subplot_adjust(self) -> dict[str, float]:
        height = self.height_cm
        panel_height = self.subplot_height_cm
        return {
            "left": self.margin_left_cm / self.plot_width_cm,
            "right": 1.0 - self.margin_right_cm / self.plot_width_cm,
            "bottom": self.margin_bottom_cm / height,
            "top": 1.0 - self.margin_top_cm / height,
            "wspace": self.space_width_cm / self.subplot_width_cm,
            "hspace": self.space_height_cm / panel_height,
        }


_PRESETS: dict[str, dict[str, float | int]] = {
    "manuscript_single": {
        "plot_width_cm": 9.0,
        "margin_left_cm": 1.5,
        "margin_right_cm": 0.4,
        "margin_bottom_cm": 1.2,
        "margin_top_cm": 0.5,
        "space_width_cm": 0.9,
        "space_height_cm": 0.8,
        "subplot_ratio": 0.78,
        "font_size": 11,
        "dpi": 300,
    },
    "manuscript_double": {
        "plot_width_cm": 18.0,
        "margin_left_cm": 1.6,
        "margin_right_cm": 0.5,
        "margin_bottom_cm": 1.3,
        "margin_top_cm": 0.6,
        "space_width_cm": 1.2,
        "space_height_cm": 0.9,
        "subplot_ratio": 0.62,
        "font_size": 11,
        "dpi": 300,
    },
    "slides_single": {
        "plot_width_cm": 15.0,
        "margin_left_cm": 2.0,
        "margin_right_cm": 0.7,
        "margin_bottom_cm": 1.7,
        "margin_top_cm": 0.7,
        "space_width_cm": 1.2,
        "space_height_cm": 1.0,
        "subplot_ratio": 0.56,
        "font_size": 17,
        "dpi": 240,
    },
    "slides_double": {
        "plot_width_cm": 24.0,
        "margin_left_cm": 2.1,
        "margin_right_cm": 0.8,
        "margin_bottom_cm": 1.8,
        "margin_top_cm": 0.8,
        "space_width_cm": 1.2,
        "space_height_cm": 1.0,
        "subplot_ratio": 0.58,
        "font_size": 17,
        "dpi": 240,
    },
    "slides_grid": {
        "plot_width_cm": 22.0,
        "margin_left_cm": 2.0,
        "margin_right_cm": 0.7,
        "margin_bottom_cm": 1.8,
        "margin_top_cm": 1.8,
        "space_width_cm": 1.4,
        "space_height_cm": 1.5,
        "subplot_ratio": 0.72,
        "font_size": 16,
        "dpi": 240,
    },
    "compact_panel": {
        "plot_width_cm": 7.0,
        "margin_left_cm": 1.2,
        "margin_right_cm": 0.25,
        "margin_bottom_cm": 0.9,
        "margin_top_cm": 0.25,
        "space_width_cm": 0.6,
        "space_height_cm": 0.6,
        "subplot_ratio": 0.82,
        "font_size": 9,
        "dpi": 300,
    },
}


def get_preset(
    name: str = "manuscript_single",
    *,
    nrows: int = 1,
    ncols: int = 1,
    **overrides,
) -> PlotSpec:
    """Return a plot specification with optional field overrides."""

    if name not in _PRESETS:
        available = ", ".join(sorted(_PRESETS))
        raise KeyError(f"unknown paperplot preset {name!r}; available presets: {available}")
    if nrows <= 0 or ncols <= 0:
        raise ValueError("nrows and ncols must be positive")
    values = dict(_PRESETS[name])
    values.update(overrides)
    return PlotSpec(name=name, nrows=nrows, ncols=ncols, **values)


def _require_latex() -> None:
    if shutil.which("latex") is None:
        raise RuntimeError(
            "paperplot requested text.usetex=True, but no 'latex' executable was found "
            "on PATH. Install a LaTeX distribution or call style_context(..., usetex=False)."
        )


def _rc_params(spec: PlotSpec) -> dict[str, object]:
    if spec.usetex:
        _require_latex()
    color_cycle = [
        "#1f77b4",
        "#d62728",
        "#2ca02c",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]
    return {
        **_FIXED_LAYOUT_PARAMS,
        "text.usetex": spec.usetex,
        "text.latex.preamble": spec.latex_preamble,
        "font.family": "serif",
        "font.size": spec.font_size,
        "axes.titlesize": spec.font_size,
        "axes.labelsize": spec.font_size,
        "xtick.labelsize": spec.font_size * 0.9,
        "ytick.labelsize": spec.font_size * 0.9,
        "legend.fontsize": spec.font_size * 0.85,
        "figure.titlesize": spec.font_size * 1.05,
        "axes.linewidth": 0.9,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.size": 4.0,
        "ytick.major.size": 4.0,
        "xtick.minor.size": 2.0,
        "ytick.minor.size": 2.0,
        "lines.linewidth": 1.5,
        "patch.linewidth": 0.8,
        "savefig.dpi": spec.dpi,
        "savefig.bbox": None,
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.prop_cycle": cycler(color=color_cycle),
    }


@contextmanager
def style_context(
    preset: str = "manuscript_single",
    *,
    nrows: int = 1,
    ncols: int = 1,
    usetex: bool = True,
    **overrides,
) -> Iterator[PlotSpec]:
    """Temporarily apply a paperplot Matplotlib style."""

    spec = get_preset(preset, nrows=nrows, ncols=ncols, usetex=usetex, **overrides)
    with plt.rc_context(_rc_params(spec)):
        yield spec


def subplots(
    nrows: int = 1,
    ncols: int = 1,
    *,
    preset: str = "manuscript_single",
    spec: PlotSpec | None = None,
    usetex: bool = True,
    **kwargs,
):
    """Create Matplotlib subplots using a ``PlotSpec`` layout."""

    for key, disabled_values in (
        ("layout", (None, "none")),
        ("tight_layout", (None, False)),
        ("constrained_layout", (None, False)),
    ):
        value = kwargs.pop(key, None)
        if value not in disabled_values:
            raise ValueError(
                f"{key}={value!r} conflicts with paperplot's fixed layout; "
                "adjust margins and spacing through PlotSpec instead"
            )
    active_spec = spec or get_preset(preset, nrows=nrows, ncols=ncols, usetex=usetex)
    subplot_adjust = active_spec.subplot_adjust
    with plt.rc_context(_FIXED_LAYOUT_PARAMS):
        fig, axes = plt.subplots(
            nrows,
            ncols,
            figsize=active_spec.figsize_inches,
            dpi=active_spec.dpi,
            **kwargs,
        )
    fig.subplots_adjust(**subplot_adjust)
    return fig, axes


def apply_axes_style(ax, *, grid: bool = True, legend_fontsize: float | None = None) -> None:
    """Apply consistent grid, tick, and legend styling to an axis."""

    ax.tick_params(which="both", direction="in", top=True, right=True)
    if grid:
        ax.grid(alpha=0.22, linewidth=0.6)
    legend = ax.get_legend()
    if legend is not None:
        legend.get_frame().set_linewidth(0.6)
        legend.get_frame().set_alpha(0.92)
        if legend_fontsize is not None:
            for text in legend.get_texts():
                text.set_fontsize(legend_fontsize)


def savefig(
    fig,
    path: str | Path,
    *,
    formats: Sequence[str] | str | None = None,
    dpi: int | None = None,
    spec: PlotSpec | None = None,
) -> list[Path]:
    """Save a figure using explicit formats, a spec's defaults, or PDF."""

    path = Path(path)
    selected_formats: tuple[str, ...]
    if formats is None:
        selected_formats = spec.default_formats if spec is not None else DEFAULT_FORMATS
    elif isinstance(formats, str):
        selected_formats = (formats,)
    else:
        selected_formats = tuple(formats)
    if not selected_formats:
        raise ValueError("formats must contain at least one file format")

    base = path.with_suffix("") if path.suffix else path
    base.parent.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    for fmt in selected_formats:
        clean_fmt = fmt.lower().lstrip(".")
        output_path = base.with_name(f"{base.name}.{clean_fmt}")
        fig.savefig(output_path, dpi=dpi)
        output_paths.append(output_path)
    return output_paths


def with_overrides(spec: PlotSpec, **overrides) -> PlotSpec:
    """Return a copy of ``spec`` with dataclass fields replaced."""

    return replace(spec, **overrides)
