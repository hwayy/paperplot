import runpy
import zipfile
from pathlib import Path

import pytest

HELPERS = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools" / "check_release.py"))


def test_release_tag_matches_package_version():
    HELPERS["check_tag"]("0.1.2", "v0.1.2")


@pytest.mark.parametrize("tag", ["v0.1.1", "0.1.2", "main"])
def test_release_rejects_mismatched_tag(tag):
    with pytest.raises(ValueError, match="does not match package version"):
        HELPERS["check_tag"]("0.1.2", tag)


def test_release_notes_only_include_the_requested_version():
    changelog = (
        "# Changes\n\n## [0.1.2] - 2026-10-17\n\n### Fixed\n\n- Current.\n\n## [0.1.1]\n\n- Old.\n"
    )
    assert HELPERS["release_notes"](changelog, "0.1.2") == "### Fixed\n\n- Current.\n"


@pytest.mark.parametrize("changelog", ["## [0.1.1]\n\n- Old.\n", "## [0.1.2]\n\n"])
def test_release_rejects_missing_or_empty_notes(changelog):
    with pytest.raises(ValueError, match="no release notes"):
        HELPERS["release_notes"](changelog, "0.1.2")


def test_release_rejects_missing_distributions(tmp_path):
    with pytest.raises(ValueError, match="exactly one wheel and one source distribution"):
        HELPERS["check_distributions"](tmp_path, "paperplot", "0.1.2")


def test_release_rejects_artifacts_from_another_version(tmp_path):
    with zipfile.ZipFile(tmp_path / "paperplot-0.1.2-py3-none-any.whl", "w") as wheel:
        wheel.writestr("paperplot-0.1.2.dist-info/METADATA", "Name: paperplot\nVersion: 0.1.1\n")
    (tmp_path / "paperplot-0.1.2.tar.gz").touch()
    with pytest.raises(ValueError, match="distribution metadata does not match"):
        HELPERS["check_distributions"](tmp_path, "paperplot", "0.1.2")
