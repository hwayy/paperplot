# Contributing

## Development

The commands below work in macOS, Linux, and Windows terminals. They assume
`python` selects Python 3.10 or newer; substitute `python3` or `py` if that is
your Python launcher.

Create a virtual environment:

```console
python -m venv .venv
```

Activate it using the [instructions for your shell](https://docs.python.org/3/library/venv.html#how-venvs-work),
then install the package and development dependencies:

```console
python -m pip install -e ".[dev]"
```

## Documentation and Agent Skill

Maintain API documentation in `docs/api.md`. Rebuild the skill reference after
editing it and include the generated file in your change:

```console
python tools/build_skill.py
python tools/build_skill.py --check
```

`--check` fails if the generated reference is missing or out of date, without
modifying files. Keep `SKILL.md` and its `references/` directory together so
skill installations work without the source checkout.

The Skills CLI discovers `.agents/skills/paperplot` directly. With Node.js
22.20+ and Git installed, check discovery from this checkout:

```console
npx skills add . --list
```

To try local skill changes, run the following from a separate project directory,
replacing `PATH_TO_PAPERPLOT` with the absolute path to this checkout:

```console
npx skills add "PATH_TO_PAPERPLOT" --skill paperplot --agent codex --copy
```

Reinstall after editing skill files. Use a GitHub source, as shown in the
[README](README.md#agent-skill), for installations managed through remote updates.

## Checks and Packaging

Run checks and build the package from the repository root:

```console
python tools/build_skill.py --check
python tools/check_release.py
python -m ruff check .
python -m pytest -W error
python -m build
python -m twine check --strict "dist/*"
python tools/check_release.py --dist dist
```

Twine expands the quoted pattern itself, so the command works in shells that
do not expand wildcards for external programs. Use a clean `dist/` directory
when preparing a release; the release checker requires exactly one wheel and
one source distribution for the current version.

Tests use `usetex=False` to avoid requiring LaTeX. With the LaTeX dependencies
listed in the [API reference](docs/api.md) installed, check rendering separately:

```console
python tools/smoke_plot.py --output-dir build/latex-smoke
```

Inspect the resulting PDF or PNG for readability, clipping, and overlap.

## CI and Releases

GitHub Actions runs documentation and release-metadata checks, Ruff, and tests
on Linux and Windows with Python 3.10 through 3.15. It also builds and checks
the wheel and source distribution, tests the installed wheel, and renders a
LaTeX figure to PDF and PNG. The `latex-preview` workflow artifact is available
for visual inspection.

The skill compatibility jobs use Node.js 24 and Skills CLI 1.7.2 on Linux and
Windows. They check local discovery and installation, then discover and install
the skill from GitHub. Remote installations are pinned to the tested commit,
including the head commit for pull requests, so later pushes cannot change the
test input. Both skill files and the remote source recorded in the lock file
are checked.

To exercise an actual update, the remote skill check replaces the installed
API reference with an older-content fixture and records its matching content
hash in the project lock. The normal `npx skills update` command must download
and restore the complete remote bundle and lock entry. A second update must
report that the skill is current and leave its files and lock unchanged.
Finally, the check removes the skill and verifies its directory, listing, and
lock entry are gone. All installation and updater state stays in temporary
directories outside the source checkout.

Separate GitHub installation jobs use fresh Python environments on Linux and
Windows. They install both the tested commit and the published `v0.1.5`
baseline through pip's GitHub URL, check package version and VCS provenance,
check dependencies, and exercise PDF/PNG export using the installed public API.
The published baseline is independent of the version being prepared, so CI
does not require a new release tag before the release can be created.

To run these network checks locally, replace `COMMIT_SHA` with a pushed commit
matching your checkout and use new directories for each run:

```console
python tools/check_github_install.py --repository hwayy/paperplot --revision COMMIT_SHA --work-dir build/github-install
python tools/check_skill_remote.py --repository hwayy/paperplot --revision COMMIT_SHA --work-dir build/remote-skills
```

To publish a GitHub release:

1. Update the version in `pyproject.toml`, the installation example in
   [README.md](README.md), and the matching entry in [CHANGELOG.md](CHANGELOG.md).
2. Run the local checks, commit the changes, and push `main`.
3. Wait for CI to pass and inspect the LaTeX preview for readability and overlap.
4. Create and push an annotated tag matching the package version. Replace
   `X.Y.Z` with the new version:

   ```console
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

The release workflow validates the tag and release notes, reruns the complete
CI workflow for that commit, and attaches the checked wheel and source
distribution to a GitHub Release. It uses the repository's `GITHUB_TOKEN` and
publishes only after all checks succeed. PyPI publishing is not configured.
