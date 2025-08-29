"""Basic video processing utilities.

This module contains minimal functionality to demonstrate how a video
can be processed into artefacts that will later become part of a SCORM
package.  The heavy lifting – high quality speech-to-text, intelligent
segmentation and quiz generation – is still to come, but the functions
below provide a scaffold that produces audio, subtitle and markdown
files from an input video.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Tuple


def extract_audio(video_path: Path, audio_path: Path) -> None:
    """Extract the audio track from ``video_path`` using ``ffmpeg``.

    The function expects ``ffmpeg`` to be available on the system.  If it
    is missing a ``FileNotFoundError`` will be raised.
    """

    cmd = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i",
        str(video_path),
        "-vn",
        str(audio_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def transcribe_audio(audio_path: Path) -> str:
    """Return a naive transcript for ``audio_path``.

    Real speech-to-text will be implemented later.  For now we just return a
    short placeholder string so downstream steps can be exercised.
    """

    return f"Transcription for {audio_path.name}."


def generate_subtitles(transcript: str) -> List[Tuple[str, str]]:
    """Create a trivial subtitle list from the transcript.

    The returned list contains tuples of ``(timestamp, text)``.  Proper
    segmentation will be added in future iterations.
    """

    return [("00:00:00,000 --> 00:00:05,000", transcript)]


def save_srt(subtitles: List[Tuple[str, str]], srt_path: Path) -> None:
    """Write a very small ``.srt`` file from ``subtitles``."""

    lines = []
    for idx, (timestamp, text) in enumerate(subtitles, start=1):
        lines.extend([str(idx), timestamp, text, ""])
    srt_path.write_text("\n".join(lines), encoding="utf-8")


def save_markdown(transcript: str, md_path: Path) -> None:
    """Persist the transcript as a markdown file."""

    md_path.write_text(transcript + "\n", encoding="utf-8")


def process_video(video_path: str, output_dir: str) -> dict:
    """Process ``video_path`` and emit basic artefacts in ``output_dir``.

    Returns a dictionary with the paths of the created files.  This minimal
    implementation is intentionally simple but establishes the foundation for
    later, more capable versions.
    """

    video = Path(video_path)
    if not video.exists():  # pragma: no cover - simple validation
        raise FileNotFoundError(f"Video file not found: {video_path}")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    audio_path = out_dir / "audio.wav"
    extract_audio(video, audio_path)

    transcript = transcribe_audio(audio_path)

    subtitles = generate_subtitles(transcript)
    srt_path = out_dir / "subtitles.srt"
    save_srt(subtitles, srt_path)

    md_path = out_dir / "transcript.md"
    save_markdown(transcript, md_path)

    return {"audio": audio_path, "srt": srt_path, "markdown": md_path}
