import subprocess
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from scorm_scorcher.video_processing import process_video


def _fake_run_factory(tmp_path: Path):
    """Create a ``subprocess.run`` replacement writing expected artefacts."""

    def _fake_run(cmd: List[str], capture_output: bool = True, text: bool = True):
        output = Path(cmd[-1])
        if "segment" in cmd:
            # create two dummy segments
            (tmp_path / "segment_000.mp4").write_text("seg0")
            (tmp_path / "segment_001.mp4").write_text("seg1")
        else:
            output.write_text("data")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    return _fake_run


def _fake_run_no_subs(tmp_path: Path):
    """A ``subprocess.run`` replacement that simulates missing subtitles."""

    def _fake_run(cmd: List[str], capture_output: bool = True, text: bool = True):
        output = Path(cmd[-1])
        if "segment" in cmd:
            (tmp_path / "segment_000.mp4").write_text("seg0")
            return subprocess.CompletedProcess(args=cmd, returncode=0)
        if output.name == "subtitles.vtt":
            # Simulate ffmpeg failing because no subtitle streams exist
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stderr="Output file does not contain any stream",
            )
        output.write_text("data")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    return _fake_run


def test_process_video_success(tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_text("data")

    with patch("scorm_scorcher.video_processing.shutil.which", return_value="ffmpeg"), \
        patch("scorm_scorcher.video_processing.subprocess.run") as mock_run:
        mock_run.side_effect = _fake_run_factory(tmp_path)
        artefacts = process_video(str(video_file), str(tmp_path))

    assert Path(artefacts["audio"]).is_file()
    assert Path(artefacts["subtitles"]).is_file()
    assert len(artefacts["segments"]) == 2
    assert mock_run.call_count == 3


def test_process_video_without_subtitles(tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_text("data")

    with patch("scorm_scorcher.video_processing.shutil.which", return_value="ffmpeg"), \
        patch("scorm_scorcher.video_processing.subprocess.run") as mock_run:
        mock_run.side_effect = _fake_run_no_subs(tmp_path)
        artefacts = process_video(str(video_file), str(tmp_path))

    assert artefacts["subtitles"] is None
    assert Path(artefacts["audio"]).is_file()
    assert len(artefacts["segments"]) == 1  # one segment was created


def test_process_video_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_video(str(tmp_path / "missing.mp4"), str(tmp_path))


def test_process_video_missing_ffmpeg(tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_text("data")

    with patch("scorm_scorcher.video_processing.shutil.which", return_value=None):
        with pytest.raises(EnvironmentError):
            process_video(str(video_file), str(tmp_path))


def test_process_video_ffmpeg_failure(tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_text("data")

    with patch("scorm_scorcher.video_processing.shutil.which", return_value="ffmpeg"), \
        patch(
            "scorm_scorcher.video_processing.subprocess.run",
            return_value=subprocess.CompletedProcess(args=[], returncode=1, stderr="boom"),
        ):
        with pytest.raises(RuntimeError):
            process_video(str(video_file), str(tmp_path))

