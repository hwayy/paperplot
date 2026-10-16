import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_committed_skill_reference_is_current():
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_skill.py"), "--check"], check=True)


def test_export_from_another_directory_and_read_only_check(tmp_path: Path):
    checkout = tmp_path / "checkout"
    tools = checkout / "tools"
    tools.mkdir(parents=True)
    script = tools / "build_skill.py"
    shutil.copyfile(ROOT / "tools" / "build_skill.py", script)
    source = checkout / "docs" / "api.md"
    source.parent.mkdir()
    source.write_text("# API\n\nFirst version.\n", encoding="utf-8")
    target = checkout / ".agents/skills/paperplot-figure-formatting/references/api.md"

    def run(*args):
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    assert run("--check").returncode == 1
    assert not target.parent.exists()
    assert run().returncode == 0
    original = target.read_bytes()
    assert "First version." in original.decode("utf-8")
    assert run("--check").returncode == 0

    source.write_text("# API\n\nUpdated version.\n", encoding="utf-8")
    assert run("--check").returncode == 1
    assert target.read_bytes() == original
    assert run().returncode == 0
    assert "Updated version." in target.read_text(encoding="utf-8")
    assert run("--check").returncode == 0
