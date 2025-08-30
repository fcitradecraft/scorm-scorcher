"""Video processing utilities using ``ffmpeg``.

This module extracts audio, subtitles and segments a video file.  The
intermediate artefacts are written to a working directory so they can be used
later when creating the SCORM package.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Dict, List


def _run_ffmpeg(cmd: List[str]) -> None:
    """Run an ``ffmpeg`` command raising :class:`RuntimeError` on failure."""

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "Unknown ffmpeg error"
        raise RuntimeError(f"ffmpeg command failed: {stderr}")


def process_video(
    video_path: str, work_dir: str, segment_duration: int = 360
) -> Dict[str, object]:
    """Process ``video_path`` writing artefacts to ``work_dir``.

    Args:
        video_path: Path to the input video file.
        work_dir: Directory where intermediate artefacts will be written.
        segment_duration: Length in seconds for each video segment.

    Returns:
        A dictionary with keys ``audio``, ``subtitles`` and ``segments``.  Each
        value is a path or list of paths to the generated artefacts.

    Raises:
        FileNotFoundError: If the video file does not exist.
        EnvironmentError: If ``ffmpeg`` is not available.
        RuntimeError: If ``ffmpeg`` fails to process the file.
    """

    src = Path(video_path)
    if not src.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    out_dir = Path(work_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("ffmpeg") is None:
        raise EnvironmentError("ffmpeg is required but was not found on the system PATH")

    # --- Extract audio ---
    audio_path = out_dir / "audio.mp3"
    audio_cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(src),
        "-vn",
        "-acodec",
        "mp3",
        str(audio_path),
    ]
    _run_ffmpeg(audio_cmd)

    # --- Extract subtitles (if available) ---
    subtitles_path = out_dir / "subtitles.vtt"
    subtitles_cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(src),
        "-map",
        "0:s:0?",
        "-f",
        "webvtt",
        str(subtitles_path),
    ]
    try:
        _run_ffmpeg(subtitles_cmd)
    except RuntimeError as exc:
        # Many videos will not contain subtitle streams.  In that case ffmpeg
        # reports ``Output file does not contain any stream``.  We treat this as
        # an optional feature and simply skip subtitle generation when no
        # subtitles are present.
        if "Output file does not contain any stream" in str(exc):
            subtitles_path = None
        else:
            raise

    # --- Segment video ---
    segment_template = out_dir / "segment_%03d.mp4"
    segment_cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(src),
        "-map",
        "0",
        "-c",
        "copy",
        "-f",
        "segment",
        "-segment_time",
        str(segment_duration),
        "-reset_timestamps",
        "1",
        str(segment_template),
    ]
    _run_ffmpeg(segment_cmd)

    segments = sorted(out_dir.glob("segment_*.mp4"))
    if not segments:
        raise RuntimeError("ffmpeg did not produce any segments")

    return {
        "audio": str(audio_path),
        "subtitles": str(subtitles_path) if subtitles_path else None,
        "segments": [str(p) for p in segments],
    }

