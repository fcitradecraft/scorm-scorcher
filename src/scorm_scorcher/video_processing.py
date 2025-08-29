"""Video processing utilities."""

from pathlib import Path
import shutil
import subprocess


def process_video(video_path: str) -> None:
    """Basic processing of a video file.

<codex/add-tests-for-process_video-and-create_scorm_package
    Validates the input file and ensures ``ffmpeg`` can read it. The command's
    stderr is surfaced to aid in debugging failed runs.
=======
    The function currently validates the input file and runs ``ffmpeg`` in a
    way that verifies the file can be read.  ``ffmpeg`` is a required external
    dependency, so the function checks that it is available before attempting
    to run it.  Any errors from the command are surfaced with their stderr
    output to aid in debugging.
> main

    Args:
        video_path: Path to the input video file.

    Raises:
        FileNotFoundError: If the video file does not exist.
        EnvironmentError: If ``ffmpeg`` is not available.
        RuntimeError: If ``ffmpeg`` fails to process the file.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if shutil.which("ffmpeg") is None:
        raise EnvironmentError("ffmpeg is required but was not found on the system PATH")

< codex/add-tests-for-process_video-and-create_scorm_package
=======
    # Run ffmpeg to validate the video. ``-f null -`` avoids creating output.
> main
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
< codex/add-tests-for-process_video-and-create_scorm_package

=======
> main
    print(f"Processing video: {video_path}")
