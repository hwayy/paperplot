"""Check that the Skills CLI installed the complete paperplot skill bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "paperplot"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("installation", type=Path, help="Installed paperplot skill directory.")
    parser.add_argument(
        "--listing", type=Path, required=True, help="Skills CLI list --json output."
    )
    args = parser.parse_args()
    installation = args.installation.resolve()
    if installation == SOURCE.resolve():
        parser.exit(1, "Check an isolated installation, not the source skill directory.\n")
    for relative in (Path("SKILL.md"), Path("references") / "api.md"):
        installed = installation / relative
        if not installed.is_file() or installed.read_text(encoding="utf-8") != (
            SOURCE / relative
        ).read_text(encoding="utf-8"):
            parser.exit(
                1, f"Installed skill file is missing or differs from the source: {relative}\n"
            )
    listing = json.loads(args.listing.read_text(encoding="utf-8-sig"))
    if not any(
        entry["name"] == "paperplot" and Path(entry["path"]).resolve() == installation
        for entry in listing
    ):
        parser.exit(1, "The Skills CLI did not list the installed paperplot skill.\n")
    print("Skills CLI installation includes paperplot instructions and the API reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
