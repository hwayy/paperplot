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
python -m pip install "paperplot @ git+ssh://git@github.com/Chiahwa/paperplot.git@v0.1.1"
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
```

`--check` fails if the generated reference is missing or out of date, without
modifying files. Tests also check the committed reference and use `usetex=False`
to avoid requiring LaTeX.

## Acknowledgements

Inspired by the centimeter-based figure sizing and publication formatting in
[`luzyPer/pyutils`](https://github.com/luzyPer/pyutils).
