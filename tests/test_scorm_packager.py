from zipfile import ZipFile

import pytest

from scorm_scorcher.scorm_packager import create_scorm_package


def _write_manifest(src):
    (src / "imsmanifest.xml").write_text("<manifest></manifest>")


def test_create_scorm_package(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "file.txt").write_text("hello")
    _write_manifest(src)
    output = tmp_path / "package.zip"

    create_scorm_package(str(src), str(output))

    assert output.exists()
    with ZipFile(output) as zf:
        assert sorted(zf.namelist()) == ["file.txt", "imsmanifest.xml"]
        assert zf.read("file.txt").decode() == "hello"


def test_create_scorm_package_missing_manifest(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    output = tmp_path / "package.zip"

    with pytest.raises(FileNotFoundError):
        create_scorm_package(str(src), str(output))
