from zipfile import ZipFile

from click.testing import CliRunner

from scorm_scorcher.cli import main


def test_cli_creates_scorm_package(tmp_path, monkeypatch):
    video = tmp_path / "video.mp4"
    video.write_text("data")
    out_dir = tmp_path / "output"

    calls = {}

    def fake_process_video(video_path, output_dir):
        calls["process_video"] = (video_path, output_dir)

    def fake_create_scorm_package(src, output_zip):
        calls["create_scorm_package"] = (src, output_zip)
        with ZipFile(output_zip, "w") as zf:
            zf.writestr("dummy.txt", "hello")

    monkeypatch.setattr("scorm_scorcher.cli.process_video", fake_process_video)
    monkeypatch.setattr("scorm_scorcher.cli.create_scorm_package", fake_create_scorm_package)

    runner = CliRunner()
    result = runner.invoke(main, [str(video), "--output-dir", str(out_dir)])

    assert result.exit_code == 0
    zip_path = out_dir / "scorm_package.zip"
    assert zip_path.exists()
    with ZipFile(zip_path) as zf:
        assert zf.namelist() == ["dummy.txt"]
    assert calls["process_video"] == (str(video), str(out_dir))
    assert calls["create_scorm_package"] == (str(out_dir), str(zip_path))
    assert f"Created SCORM package at {zip_path}" in result.output
