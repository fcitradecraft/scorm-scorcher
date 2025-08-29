"""Video processing utilities."""

from pathlib import Path
import subprocess


def process_video(video_path: str) -> None:
    """Run a dummy ffmpeg command to validate video input.

    Args:
        video_path: Path to the input video file.

    Raises:
        FileNotFoundError: If the video file does not exist.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    subprocess.run(
        ["ffmpeg", "-i", str(path), "-f", "null", "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
