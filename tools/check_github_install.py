"""Install paperplot from GitHub into a fresh environment and check its provenance."""

from __future__ import annotations

import argparse
import os
import subprocess
import venv
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="GitHub owner/repository.")
    parser.add_argument("--revision", required=True, help="Remote commit or release tag.")
    parser.add_argument("--version", help="Expected version; defaults to this checkout's version.")
    parser.add_argument("--work-dir", required=True, type=Path, help="New isolated directory.")
    args = parser.parse_args()
    version = (
        args.version
        or tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
            "version"
        ]
    )
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=False)
    consumer = work / "consumer"
    consumer.mkdir()
    temporary = work / "tmp"
    temporary.mkdir()
    env = {
        **os.environ,
        "TMP": str(temporary),
        "TEMP": str(temporary),
        "MPLCONFIGDIR": str(work / "mplconfig"),
        "MPLBACKEND": "Agg",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONNOUSERSITE": "1",
    }
    env.pop("PYTHONPATH", None)
    environment = work / "venv"
    # ensurepip also needs the isolated temporary directory on Windows.
    os.environ.update({"TMP": str(temporary), "TEMP": str(temporary)})
    venv.create(environment, with_pip=True)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    url = f"https://github.com/{args.repository}.git"
    subprocess.run(
        [str(python), "-m", "pip", "install", f"paperplot @ git+{url}@{args.revision}"],
        cwd=consumer,
        env=env,
        check=True,
    )
    subprocess.run([str(python), "-m", "pip", "check"], cwd=consumer, env=env, check=True)
    # Run outside the checkout, using only the installed package and public API.
    probe = r"""
import json
import sys
from importlib.metadata import distribution
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import paperplot
from paperplot import apply_axes_style, savefig, style_context, subplots

url, revision, version, environment = sys.argv[1:]
dist = distribution("paperplot")
direct = json.loads(dist.read_text("direct_url.json"))
assert dist.version == version, dist.version
assert Path(paperplot.__file__).resolve().is_relative_to(Path(environment).resolve())
assert direct["url"] == url, direct
assert direct["vcs_info"]["requested_revision"] == revision, direct
if len(revision) == 40:
    assert direct["vcs_info"]["commit_id"] == revision, direct
with style_context("manuscript_single", usetex=False, default_formats=("pdf", "png")) as spec:
    fig, ax = subplots(spec=spec, usetex=False)
    ax.plot([0, 1, 2], [0, 1, 4])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    apply_axes_style(ax)
    paths = savefig(fig, "results/github-install", spec=spec)
    assert {p.suffix for p in paths} == {".pdf", ".png"}, paths
    assert all(p.stat().st_size > 0 for p in paths)
    assert Path("results/github-install.pdf").read_bytes().startswith(b"%PDF-")
    assert plt.imread("results/github-install.png").size > 0
    plt.close(fig)
print(json.dumps({"version": dist.version, "import": paperplot.__file__, "source": direct}, indent=2))
"""
    subprocess.run(
        [str(python), "-W", "error", "-c", probe, url, args.revision, version, str(environment)],
        cwd=consumer,
        env=env,
        check=True,
    )
    print(f"GitHub installation and PDF/PNG export passed for {args.revision}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
