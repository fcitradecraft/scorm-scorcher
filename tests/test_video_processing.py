"""Tests for video_processing.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scorm_scorcher.video_processing import _is_url, process_video


def test_is_url():
    assert _is_url("https://example.com/video.mp4")
    assert _is_url("http://example.com/video.mp4")
    assert not _is_url("/local/path/video.mp4")
    assert not _is_url("relative/path.mp4")


def test_missing_local_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_video("/nonexistent/video.mp4", str(tmp_path))


def test_missing_ffmpeg_raises(tmp_path, monkeypatch):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"")
    monkeypatch.setattr("shutil.which", lambda _: None)
    with pytest.raises(EnvironmentError, match="ffmpeg"):
        process_video(str(video), str(tmp_path))


def test_ffmpeg_audio_failure_raises(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"fake")
    with patch("scorm_scorcher.video_processing.shutil.which", return_value="/usr/bin/ffmpeg"):
        with patch("scorm_scorcher.video_processing._run_ffmpeg", side_effect=RuntimeError("ffmpeg failed")):
            with pytest.raises(RuntimeError, match="ffmpeg failed"):
                process_video(str(video), str(tmp_path))


def test_url_triggers_download(tmp_path):
    with patch("scorm_scorcher.video_processing.shutil.which", return_value="/usr/bin/ffmpeg"):
        with patch("scorm_scorcher.video_processing._download_video") as mock_dl:
            with patch("scorm_scorcher.video_processing._run_ffmpeg") as mock_ffmpeg:
                # Make the downloaded file appear to exist
                fake_src = tmp_path / "_source.mp4"
                fake_src.write_bytes(b"")

                def fake_download(url, dest):
                    dest.write_bytes(b"")

                mock_dl.side_effect = fake_download
                # Suppress subtitle extraction "no stream" error gracefully
                mock_ffmpeg.side_effect = [
                    None,  # audio extraction
                    RuntimeError("Output file does not contain any stream"),  # subtitles
                    None,  # segmentation
                ]
                # Create fake segment
                (tmp_path / "segment_000.mp4").write_bytes(b"")

                result = process_video("https://example.com/v.mp4", str(tmp_path))
                mock_dl.assert_called_once()
                assert "audio" in result
