import subprocess
from unittest.mock import patch

from scorm_scorcher.video_processing import process_video


def test_process_video_calls_ffmpeg(tmp_path):
    video_file = tmp_path / "video.mp4"
    video_file.write_text("data")

    with patch("scorm_scorcher.video_processing.shutil.which", return_value="ffmpeg"), \
        patch("scorm_scorcher.video_processing.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        process_video(str(video_file))

    mock_run.assert_called_once_with(
        ["ffmpeg", "-v", "error", "-i", str(video_file), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
