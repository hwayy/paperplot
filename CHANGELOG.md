# Changelog

## [0.1.5] - 2026-10-17

- Move contributor instructions into `CONTRIBUTING.md` and use portable command examples.
- Document Skills CLI installation and management, with Linux/Windows checks
  that verify discovery, complete reference installation, listing, and removal.

## [0.1.2] - 2026-10-17

### Fixed

- Preserve intermediate filename suffixes during export, so `chart.v1.pdf`
  and `chart.v2.pdf` remain separate files.
- Recompute panel heights when `plot_height_cm` is specified, preserving
  centimeter margins and gaps. Heights without room for panels raise `ValueError`.
- Disable inherited Matplotlib automatic layout settings to preserve fixed
  geometry. Explicit automatic layout options now raise `ValueError`; use
  `PlotSpec` margins and spacing instead.

### Added

- `savefig(..., spec=spec)` uses `spec.default_formats` when `formats` is omitted.
  Explicit `formats` takes precedence; calls without a spec still default to PDF.
- A portable `paperplot` agent skill with an API reference generated from
  `docs/api.md` and included in source distributions.
- CI for Linux and Windows on Python 3.10-3.15, distribution validation,
  installed-wheel tests, and LaTeX PDF/PNG rendering checks.
- GitHub releases from version tags, gated by the complete CI workflow and
  tag/version validation, with wheel and source-distribution attachments.
