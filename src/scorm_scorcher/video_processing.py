"""Video processing utilities."""

from pathlib import Path
import shutil
import subprocess


def process_video(video_path: str) -> None:
    """Basic processing of a video file.

    The function currently validates the input file and runs ``ffmpeg`` in a
    way that verifies the file can be read.  ``ffmpeg`` is a required external
    dependency, so the function checks that it is available before attempting
    to run it.  Any errors from the command are surfaced with their stderr
    output to aid in debugging.

    Args:
        video_path: Path to the input video file.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if shutil.which("ffmpeg") is None:
        raise EnvironmentError("ffmpeg is required but was not found on the system PATH")

    # Run ffmpeg to validate the video. ``-f null -`` avoids creating output.
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(path),
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "Unknown ffmpeg error"
        raise RuntimeError(f"ffmpeg failed to process '{video_path}': {stderr}")
    print(f"Processing video: {video_path}")
