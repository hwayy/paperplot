"""Validate release metadata and the distributions that will be published."""

from __future__ import annotations

import argparse
import re
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 development environments.
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def check_tag(version: str, tag: str) -> None:
    if tag != f"v{version}":
        raise ValueError(f"tag {tag!r} does not match package version v{version}")


def release_notes(changelog: str, version: str) -> str:
    section = re.search(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## |\Z)",
        changelog,
        flags=re.MULTILINE | re.DOTALL,
    )
    if section is None or not section.group(1).strip():
        raise ValueError(f"CHANGELOG.md has no release notes for {version}")
    return section.group(1).strip() + "\n"


def check_distributions(directory: Path, name: str, version: str) -> None:
    wheels = sorted(directory.glob("*.whl"))
    sources = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise ValueError("release must contain exactly one wheel and one source distribution")

    def check_metadata(content: bytes) -> None:
        metadata = BytesParser().parsebytes(content)
        if metadata["Name"] != name or metadata["Version"] != version:
            raise ValueError(f"distribution metadata does not match {name} {version}")

    with zipfile.ZipFile(wheels[0]) as wheel:
        metadata_paths = [p for p in wheel.namelist() if p.endswith(".dist-info/METADATA")]
        if len(metadata_paths) != 1:
            raise ValueError("wheel must contain one METADATA file")
        check_metadata(wheel.read(metadata_paths[0]))
        required = {"paperplot/__init__.py", "paperplot/style.py"}
        if not required.issubset(wheel.namelist()):
            raise ValueError("wheel is missing paperplot modules")
        if not any(p.endswith(".dist-info/licenses/LICENSE") for p in wheel.namelist()):
            raise ValueError("wheel is missing its license")

    prefix = f"{name}-{version}/"
    required = {
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "pyproject.toml",
        "docs/api.md",
        "tools/build_skill.py",
        "tools/check_release.py",
        "tools/smoke_plot.py",
        ".agents/skills/paperplot/SKILL.md",
        ".agents/skills/paperplot/references/api.md",
    }
    with tarfile.open(sources[0]) as source:
        missing = {prefix + path for path in required} - set(source.getnames())
        if missing:
            raise ValueError(f"source distribution is missing: {', '.join(sorted(missing))}")
        metadata = source.extractfile(prefix + "PKG-INFO")
        if metadata is None:
            raise ValueError("source distribution is missing PKG-INFO")
        check_metadata(metadata.read())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Require a version tag matching pyproject.toml.")
    parser.add_argument("--dist", type=Path, help="Check built wheel and source distribution.")
    parser.add_argument("--notes-file", type=Path, help="Write the matching changelog entry.")
    args = parser.parse_args()
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    try:
        if args.tag is not None:
            check_tag(version, args.tag)
        notes = release_notes((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version)
        if args.dist is not None:
            check_distributions(args.dist, project["name"], version)
    except ValueError as error:
        parser.exit(1, f"{error}\n")
    if args.notes_file is not None:
        args.notes_file.write_text(notes, encoding="utf-8", newline="\n")
    print(f"Release checks passed for v{version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
