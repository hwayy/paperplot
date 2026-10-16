"""Render a LaTeX figure and verify physical geometry, text bounds, and exports."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paperplot import apply_axes_style, savefig, style_context, subplots


def require_close(actual: float, expected: float, name: str, *, tolerance: float = 1e-6) -> None:
    if not math.isclose(actual, expected, abs_tol=tolerance):
        raise RuntimeError(f"{name}: expected {expected}, got {actual}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("build/latex-smoke"))
    args = parser.parse_args()
    with (
        plt.rc_context({"figure.autolayout": True, "figure.constrained_layout.use": True}),
        style_context(
            "slides_grid", nrows=2, ncols=2, plot_height_cm=12, default_formats=("pdf", "png")
        ) as spec,
    ):
        fig, axes = subplots(2, 2, spec=spec, sharex=True)
        try:
            for index, ax in enumerate(axes.flat, 1):
                ax.plot([0, 1, 2], [0, index, 4 * index], label=rf"$\bm{{y}}={index}x^2$")
                if index > 2:
                    ax.set_xlabel(r"$x$")
                ax.set_ylabel(r"$y$")
                ax.set_title(f"Panel {index}")
                ax.legend()
                apply_axes_style(ax)
            fig.canvas.draw()
            upper, lower = axes[0, 0].get_position(), axes[1, 0].get_position()
            require_close(upper.x0 * spec.plot_width_cm, spec.margin_left_cm, "left margin")
            require_close((upper.y0 - lower.y1) * spec.height_cm, spec.space_height_cm, "row gap")
            renderer = fig.canvas.get_renderer()
            texts = []
            for index, ax in enumerate(axes.flat):
                artists = [ax.title, ax.xaxis.label, ax.yaxis.label, ax.get_legend()]
                for axis in (ax.xaxis, ax.yaxis):
                    low, high = sorted(axis.get_view_interval())
                    for tick in axis.get_major_ticks():
                        if low <= tick.get_loc() <= high:
                            artists.extend((tick.label1, tick.label2))
                for artist in artists:
                    if not artist.get_visible():
                        continue
                    if hasattr(artist, "get_text") and not artist.get_text():
                        continue
                    bbox = artist.get_window_extent(renderer)
                    if not (fig.bbox.contains(*bbox.p0) and fig.bbox.contains(*bbox.p1)):
                        raise RuntimeError(f"text or legend extends beyond the figure: {artist}")
                    texts.append((index, bbox))
            for i, (panel, bbox) in enumerate(texts):
                for other_panel, other_bbox in texts[i + 1 :]:
                    if panel != other_panel and bbox.overlaps(other_bbox):
                        raise RuntimeError("text or legends overlap between panels")
            paths = []
            for version in ("v1", "v2"):
                paths.extend(savefig(fig, args.output_dir / f"chart.{version}.pdf", spec=spec))
            if len(set(paths)) != 4:
                raise RuntimeError("versioned export filenames collide")
            for path in paths:
                if path.suffix == ".png":
                    image = plt.imread(path)
                    require_close(
                        image.shape[1],
                        spec.figsize_inches[0] * spec.dpi,
                        "PNG width",
                        tolerance=1,
                    )
                    require_close(
                        image.shape[0],
                        spec.figsize_inches[1] * spec.dpi,
                        "PNG height",
                        tolerance=1,
                    )
                else:
                    data = path.read_bytes()
                    match = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", data)
                    if not data.startswith(b"%PDF-") or match is None:
                        raise RuntimeError("PDF export is missing its header or page dimensions")
                    require_close(float(match[1]), spec.figsize_inches[0] * 72, "PDF width")
                    require_close(float(match[2]), spec.figsize_inches[1] * 72, "PDF height")
                print(f"Checked {path}")
        finally:
            plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
