from zipfile import ZipFile

from scorm_scorcher.scorm_packager import create_scorm_package


def test_create_scorm_package(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "file.txt").write_text("hello")
    output = tmp_path / "package.zip"

    create_scorm_package(str(src), str(output))

    assert output.exists()
    with ZipFile(output) as zf:
        assert zf.namelist() == ["file.txt"]
        assert zf.read("file.txt").decode() == "hello"
