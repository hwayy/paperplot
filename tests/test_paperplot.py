from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paperplot import get_preset, savefig, style_context, subplots


def test_preset_computes_positive_panel_geometry():
    spec = get_preset("slides_grid", nrows=2, ncols=2, usetex=False)

    assert spec.plot_width_cm == 22.0
    assert spec.subplot_width_cm > 0.0
    assert spec.subplot_height_cm > 0.0
    assert spec.height_cm > spec.subplot_height_cm
    assert spec.figsize_inches[0] == spec.plot_width_cm / 2.54


def test_style_context_sets_rcparams_without_latex():
    with style_context("manuscript_single", usetex=False, font_size=13) as spec:
        assert spec.font_size == 13
        assert plt.rcParams["text.usetex"] is False
        assert plt.rcParams["font.size"] == 13


def test_subplots_uses_spec_layout():
    with style_context("slides_grid", nrows=2, ncols=2, usetex=False) as spec:
        fig, axes = subplots(2, 2, spec=spec, sharex=True)
        try:
            assert len(axes.ravel()) == 4
            width, height = fig.get_size_inches()
            assert width == spec.figsize_inches[0]
            assert height == spec.figsize_inches[1]
        finally:
            plt.close(fig)


def test_savefig_defaults_to_pdf_and_supports_png(tmp_path: Path):
    with style_context("compact_panel", usetex=False) as spec:
        fig, ax = subplots(spec=spec)
        try:
            ax.plot([0, 1], [0, 1])
            default_paths = savefig(fig, tmp_path / "line")
            explicit_paths = savefig(fig, tmp_path / "line_copy", formats=("pdf", "png"))
        finally:
            plt.close(fig)

    assert default_paths == [tmp_path / "line.pdf"]
    assert (tmp_path / "line.pdf").exists()
    assert explicit_paths == [tmp_path / "line_copy.pdf", tmp_path / "line_copy.png"]
    assert (tmp_path / "line_copy.png").exists()


def test_savefig_keeps_versioned_filenames_distinct(tmp_path: Path):
    with style_context("compact_panel", usetex=False) as spec:
        fig, ax = subplots(spec=spec)
        try:
            ax.plot([0, 1], [0, 1])
            paths = []
            for version in ("v1", "v2"):
                paths.extend(
                    savefig(
                        fig,
                        tmp_path / "nested" / f"chart.{version}.pdf",
                        formats=("pdf", "png"),
                    )
                )
        finally:
            plt.close(fig)

    expected = [
        tmp_path / "nested" / f"chart.{version}.{fmt}"
        for version in ("v1", "v2")
        for fmt in ("pdf", "png")
    ]
    assert paths == expected
    assert all(path.is_file() for path in expected)


@pytest.mark.parametrize("height", [None, 12.0, 20.0])
@pytest.mark.parametrize("nrows", [1, 2, 3])
def test_subplots_preserves_physical_geometry_with_height_override(height, nrows):
    spec = get_preset("slides_grid", nrows=nrows, ncols=2, plot_height_cm=height, usetex=False)
    fig, axes = subplots(nrows, 2, spec=spec, squeeze=False)
    try:
        figure_width, figure_height = fig.get_size_inches() * 2.54
        if height is not None:
            assert figure_height == pytest.approx(height)
        top_left = axes[0, 0].get_position()
        bottom_left = axes[-1, 0].get_position()
        assert top_left.x0 * figure_width == pytest.approx(spec.margin_left_cm)
        assert (1 - axes[0, -1].get_position().x1) * figure_width == pytest.approx(
            spec.margin_right_cm
        )
        assert (1 - top_left.y1) * figure_height == pytest.approx(spec.margin_top_cm)
        assert bottom_left.y0 * figure_height == pytest.approx(spec.margin_bottom_cm)
        assert top_left.height * figure_height == pytest.approx(spec.subplot_height_cm)
        assert top_left.width * figure_width == pytest.approx(spec.subplot_width_cm)
        assert (axes[0, 1].get_position().x0 - top_left.x1) * figure_width == pytest.approx(
            spec.space_width_cm
        )
        for upper, lower in zip(axes[:-1, 0], axes[1:, 0]):
            gap = upper.get_position().y0 - lower.get_position().y1
            assert gap * figure_height == pytest.approx(spec.space_height_cm)
    finally:
        plt.close(fig)


@pytest.mark.parametrize("height", [0.0, 3.6, 5.1])
def test_subplots_rejects_height_without_room_for_panels(height):
    spec = get_preset("slides_grid", nrows=2, ncols=2, plot_height_cm=height, usetex=False)
    existing_figures = plt.get_fignums()
    with pytest.raises(ValueError, match="subplot height must be positive"):
        subplots(2, 2, spec=spec)
    assert plt.get_fignums() == existing_figures


@pytest.mark.parametrize("autolayout,constrained", [(True, False), (False, True), (True, True)])
def test_style_context_disables_and_restores_automatic_layout(autolayout, constrained):
    settings = {
        "figure.autolayout": autolayout,
        "figure.constrained_layout.use": constrained,
    }
    with plt.rc_context(settings):
        with style_context(usetex=False):
            assert plt.rcParams["figure.autolayout"] is False
            assert plt.rcParams["figure.constrained_layout.use"] is False
        for key, value in settings.items():
            assert plt.rcParams[key] is value


@pytest.mark.parametrize("autolayout,constrained", [(True, False), (False, True), (True, True)])
def test_subplots_preserves_margins_after_draw_with_inherited_layout(autolayout, constrained):
    settings = {
        "figure.autolayout": autolayout,
        "figure.constrained_layout.use": constrained,
        "text.usetex": False,
    }
    spec = get_preset("slides_grid", nrows=2, ncols=2, usetex=False)
    with plt.rc_context(settings):
        fig, axes = subplots(2, 2, spec=spec)
        try:
            fig.canvas.draw()
            upper = axes[0, 0].get_position()
            lower = axes[1, 0].get_position()
            assert upper.x0 * spec.plot_width_cm == pytest.approx(spec.margin_left_cm)
            assert (upper.y0 - lower.y1) * spec.height_cm == pytest.approx(spec.space_height_cm)
            for key, value in settings.items():
                assert plt.rcParams[key] is value
        finally:
            plt.close(fig)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"layout": "tight"},
        {"layout": "constrained"},
        {"layout": "compressed"},
        {"tight_layout": True},
        {"tight_layout": {}},
        {"constrained_layout": True},
        {"constrained_layout": {"h_pad": 0.1}},
    ],
)
def test_subplots_rejects_explicit_automatic_layout(kwargs):
    existing_figures = plt.get_fignums()
    with pytest.raises(ValueError, match="conflicts with paperplot's fixed layout"):
        subplots(usetex=False, **kwargs)
    assert plt.get_fignums() == existing_figures


@pytest.mark.parametrize(
    "kwargs",
    [
        {"layout": None},
        {"layout": "none"},
        {"tight_layout": False},
        {"constrained_layout": False},
        {"layout": "none", "tight_layout": False, "constrained_layout": False},
    ],
)
def test_subplots_accepts_disabled_layout_options(kwargs):
    with plt.rc_context({"figure.autolayout": True, "text.usetex": False}):
        fig, ax = subplots(usetex=False, **kwargs)
        try:
            fig.canvas.draw()
            assert ax.get_position().x0 * 9.0 == pytest.approx(1.5)
        finally:
            plt.close(fig)


@pytest.mark.parametrize(
    "formats,expected_formats",
    [(None, ("png", "pdf")), ("pdf", ("pdf",)), (("png",), ("png",))],
)
def test_savefig_uses_spec_defaults_unless_formats_are_explicit(tmp_path, formats, expected_formats):
    with style_context("compact_panel", usetex=False, default_formats=("png", "pdf")) as spec:
        fig, ax = subplots(spec=spec)
        try:
            ax.plot([0, 1], [0, 1])
            paths = savefig(fig, tmp_path / "custom", spec=spec, formats=formats)
        finally:
            plt.close(fig)

    assert paths == [tmp_path / f"custom.{fmt}" for fmt in expected_formats]
    assert all(path.is_file() for path in paths)


def test_savefig_rejects_empty_spec_formats(tmp_path):
    spec = get_preset(default_formats=(), usetex=False)
    fig, _ = subplots(spec=spec)
    try:
        with pytest.raises(ValueError, match="formats must contain at least one"):
            savefig(fig, tmp_path / "empty", spec=spec)
    finally:
        plt.close(fig)
