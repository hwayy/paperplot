# paperplot

`paperplot` provides Matplotlib presets for research figures, with
centimeter-based layouts, LaTeX text, and PDF export by default.

See the [API reference and example](docs/api.md) for presets, layout overrides,
LaTeX requirements, and usage.

## Installation

From a local checkout:

```powershell
python -m pip install .
```

From GitHub:

```powershell
python -m pip install "paperplot @ git+https://github.com/hwayy/paperplot.git@v0.1.2"
```

## Agent Skill

The [paperplot skill](.agents/skills/paperplot/SKILL.md)
provides plotting workflows and checks. Install the entire
`.agents/skills/paperplot` directory, including `references/`.
The skill requires `paperplot` in the active Python environment.

For local development, a directory junction keeps the installed skill in sync
with this checkout:

```powershell
$paperplotCheckout = (Get-Location).Path
New-Item -ItemType Directory -Path (Join-Path $HOME ".agents/skills") -Force
New-Item -ItemType Junction `
  -Path (Join-Path $HOME ".agents/skills/paperplot") `
  -Target (Join-Path $paperplotCheckout ".agents/skills/paperplot")
```

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Maintain API documentation in `docs/api.md`. Rebuild the skill reference after
editing it and commit the generated file so installs from Git remain complete:

```powershell
python tools/build_skill.py
```

Run checks and build the package:

```powershell
python tools/build_skill.py --check
python -m ruff check .
python -m pytest
python -m build
python -m twine check --strict dist/*
python tools/check_release.py --dist dist
```

`--check` fails if the generated reference is missing or out of date, without
modifying files. Tests also check the committed reference and use `usetex=False`
to avoid requiring LaTeX.

## CI and Releases

GitHub Actions runs documentation and release-metadata checks, Ruff, and tests
on Linux and Windows with Python 3.10 through 3.15. It also builds and checks
the wheel and source distribution, tests the installed wheel, and renders a
LaTeX figure to PDF and PNG. The `latex-preview` workflow artifact is available
for visual inspection.

To publish a GitHub release:

1. Update the version in `pyproject.toml`, the installation example above, and
   the matching entry in [CHANGELOG.md](CHANGELOG.md).
2. Run the local checks, commit the changes, and push `main`.
3. Wait for CI to pass and inspect the LaTeX preview for readability and overlap.
4. Create and push an annotated tag matching the package version:

   ```powershell
   git tag -a v0.1.2 -m "Release v0.1.2"
   git push origin v0.1.2
   ```

The release workflow validates the tag and release notes, reruns the complete
CI workflow for that commit, and attaches the checked wheel and source
distribution to a GitHub Release. It uses the repository's `GITHUB_TOKEN` and
publishes only after all checks succeed. PyPI publishing is not configured.

## Acknowledgements

Inspired by the centimeter-based figure sizing and publication formatting in
[`luzyPer/pyutils`](https://github.com/luzyPer/pyutils).
