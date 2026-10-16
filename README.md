# paperplot

`paperplot` provides Matplotlib presets for research figures, with
centimeter-based layouts, LaTeX text, and PDF export by default.

See the [API reference and example](docs/api.md) for presets, layout overrides,
LaTeX requirements, and usage.

## Installation

Requires Python 3.10+. The commands use `python`; use `python3` or `py` if that
is your Python launcher. Installing from GitHub also requires Git.

From a local checkout:

```console
python -m pip install .
```

From GitHub:

```console
python -m pip install "paperplot @ git+https://github.com/hwayy/paperplot.git@v0.1.6"
```

## Agent Skill

The [paperplot skill](.agents/skills/paperplot/SKILL.md) provides plotting
workflows and checks for coding agents. Install it with the
[Skills CLI](https://github.com/vercel-labs/skills), using Node.js 22.20+ and Git:

```console
npx skills add hwayy/paperplot --skill paperplot
```

Run this from the project where you want to use the skill. The CLI installs
the complete skill directory, including its API reference, and lets you select
your coding agents. Add `--agent codex` to target Codex, or `--global` to install
for use across projects. The repository's `.agents/skills/` layout is supported
directly by the CLI.

Manage project-installed skills from the same project directory:

```console
npx skills list
npx skills update paperplot --project
npx skills remove paperplot
```

For global installations, add `--global` to `list` and `remove`, and replace
`--project` with `--global` for `update`. Skill installation is separate from the
Python package: install `paperplot` in the Python environment used by your
plotting code, using the installation command above.

Development, documentation maintenance, CI, and release instructions are in
the [contributor guide](CONTRIBUTING.md).

## Acknowledgements

Inspired by the centimeter-based figure sizing and publication formatting in
[`luzyPer/pyutils`](https://github.com/luzyPer/pyutils).
