"""Exercise remote Skills CLI installation, a real refresh, and an unchanged update."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = Path(".agents/skills/paperplot")


def snapshot(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file()
    }


def main() -> int:
    # Skills CLI uses Unicode decorations that Windows' legacy code pages omit.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="GitHub owner/repository.")
    parser.add_argument("--revision", required=True, help="Remote commit matching the checkout.")
    parser.add_argument("--skills-version", default="1.7.2")
    parser.add_argument("--work-dir", required=True, type=Path, help="New isolated directory.")
    args = parser.parse_args()
    work = args.work_dir.resolve()
    project = work / "consumer"
    work.mkdir(parents=True, exist_ok=False)
    project.mkdir()
    temporary = work / "tmp"
    temporary.mkdir()
    env = {
        **os.environ,
        "TMP": str(temporary),
        "TEMP": str(temporary),
        "XDG_STATE_HOME": str(work / "state"),
        "DISABLE_TELEMETRY": "1",
        "GH_HOST": "github.com",
    }
    npx = shutil.which("npx.cmd" if os.name == "nt" else "npx")
    if npx is None:
        parser.error("Node.js and npx must be installed.")

    def skills(*arguments: str) -> str:
        result = subprocess.run(
            [npx, "--yes", f"skills@{args.skills_version}", *arguments],
            cwd=project,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        print(result.stdout, end="", flush=True)
        print(result.stderr, end="", flush=True)
        result.check_returncode()
        return result.stdout

    # Exercise the README's owner/repo shorthand as well as the pinned install.
    discovery = skills("add", args.repository, "--list")
    if "paperplot" not in discovery:
        raise RuntimeError("Remote discovery did not find paperplot.")
    source = f"https://github.com/{args.repository}/tree/{args.revision}"
    skills("add", source, "--skill", "paperplot", "--agent", "codex", "--yes")
    installation = project / SKILL_PATH

    def check_installation() -> None:
        listed = json.loads(skills("list", "--json"))
        if not any(
            entry["name"] == "paperplot"
            and entry["scope"] == "project"
            and Path(entry["path"]).resolve() == installation
            for entry in listed
        ):
            raise RuntimeError("Remote skill installation was not listed in this project.")
        expected = snapshot(ROOT / SKILL_PATH)
        actual = snapshot(installation)
        if {name: data.replace(b"\r\n", b"\n") for name, data in actual.items()} != {
            name: data.replace(b"\r\n", b"\n") for name, data in expected.items()
        }:
            raise RuntimeError("Remote skill bundle differs from the tested checkout.")

    check_installation()
    lock_path = project / "skills-lock.json"
    original_lock = json.loads(lock_path.read_text(encoding="utf-8"))
    entry = original_lock["skills"]["paperplot"]
    if (entry["source"], entry["sourceType"], entry.get("ref"), entry.get("skillPath")) != (
        args.repository,
        "github",
        args.revision,
        ".agents/skills/paperplot/SKILL.md",
    ):
        raise RuntimeError(f"Unexpected remote source tracking: {entry}")
    original_files = snapshot(installation)

    # Model an older installed snapshot without publishing a temporary remote commit.
    # Its lock hash must describe its contents, as it would after a normal old install.
    (installation / "references/api.md").write_text(
        "# Older API reference fixture\n\nThis snapshot must be replaced by update.\n",
        encoding="utf-8",
    )
    hash_script = r"""
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = process.argv[1], files = [];
function collect(dir) {
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory() && !['.git', 'node_modules'].includes(entry.name)) collect(file);
    else if (entry.isFile()) files.push({name: path.relative(root, file).split(path.sep).join('/'),
                                       data: fs.readFileSync(file)});
  }
}
collect(root);
files.sort((a, b) => a.name.localeCompare(b.name));
const hash = crypto.createHash('sha256');
for (const file of files) { hash.update(file.name); hash.update(file.data); }
console.log(hash.digest('hex'));
"""
    stale_hash = subprocess.check_output(
        ["node", "-e", hash_script, str(installation)], env=env, text=True
    ).strip()
    if stale_hash == entry["computedHash"]:
        raise RuntimeError("The old snapshot did not change the tracked content hash.")
    stale_lock = json.loads(lock_path.read_text(encoding="utf-8"))
    stale_lock["skills"]["paperplot"]["computedHash"] = stale_hash
    lock_path.write_text(json.dumps(stale_lock, indent=2) + "\n", encoding="utf-8")

    updated = skills("update", "paperplot", "--project", "--yes")
    if "Updated 1 skill(s)" not in updated:
        raise RuntimeError("The stale installation was not actually updated.")
    check_installation()
    if snapshot(installation) != original_files:
        raise RuntimeError("Update did not restore the full original skill bundle.")
    if json.loads(lock_path.read_text(encoding="utf-8")) != original_lock:
        raise RuntimeError("Update did not restore the expected lock entry and source.")

    before = {path: path.stat().st_mtime_ns for path in installation.rglob("*") if path.is_file()}
    lock_bytes = lock_path.read_bytes()
    repeated = skills("update", "paperplot", "--project", "--yes")
    if "All project skills are up to date" not in repeated or "Updated 1 skill(s)" in repeated:
        raise RuntimeError("Repeated update was not recognized as already current.")
    if snapshot(installation) != original_files or lock_path.read_bytes() != lock_bytes:
        raise RuntimeError("Repeated update changed skill contents or the lock file.")
    if any(path.stat().st_mtime_ns != stamp for path, stamp in before.items()):
        raise RuntimeError("Repeated update unnecessarily rewrote the installed files.")

    skills("remove", "paperplot", "--yes")
    if installation.exists() or json.loads(skills("list", "--json")):
        raise RuntimeError("Remote skill was not completely removed.")
    if "paperplot" in json.loads(lock_path.read_text(encoding="utf-8"))["skills"]:
        raise RuntimeError("Removed skill still appears in the lock file.")
    print("Remote install, actual update, unchanged repeat, and removal all passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
