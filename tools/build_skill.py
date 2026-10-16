"""Export the canonical API documentation into the distributable skill."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "api.md"
TARGET = ROOT / ".agents" / "skills" / "paperplot" / "references" / "api.md"
HEADER = "<!-- Generated from docs/api.md by tools/build_skill.py. Do not edit directly. -->\n\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check freshness without writing files.")
    args = parser.parse_args()
    expected = HEADER + SOURCE.read_text(encoding="utf-8")

    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != expected:
            parser.exit(1, "Skill reference is missing or stale. Run python tools/build_skill.py.\n")
        print("Skill reference is up to date.")
        return 0

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Generated {TARGET.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
