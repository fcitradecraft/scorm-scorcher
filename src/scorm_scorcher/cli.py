"""Command-line interface: prepare → quiz → build → package."""

from __future__ import annotations

import shutil
from pathlib import Path

import click

from .builder import QUIZ_HTML_NAME, QUIZ_JSON_NAME, generate_manifest, generate_player_html, generate_quiz_html
from .quiz_generation import generate_quiz_from_transcript, save_quiz_to_json, save_quiz_to_xlsx
from .scorm_packager import create_scorm_package
from .transcript import (
    auto_generate_sections,
    generate_markdown,
    load_sections,
    parse_srt,
    save_sections,
)
from .transcription import transcribe_to_srt
from .video_processing import process_video


@click.group()
@click.version_option()
def main() -> None:
    """Convert video files into SCORM 1.2 packages.

    Typical workflow:

    \b
        scorm-scorcher prepare --video lesson.mp4 --output ./build
        scorm-scorcher quiz    --input ./build
        scorm-scorcher build   --video lesson.mp4 --input ./build --title "My Lesson"
        scorm-scorcher package --input ./build --title "My Lesson"
    """


@main.command()
@click.option("--video", required=True, help="Local path or HTTP(S) URL to the video file.")
@click.option("--output", required=True, help="Output directory for processed assets.")
@click.option("--subtitles", default=None, help="Path to an existing .srt subtitle file (skips Whisper).")
@click.option("--interval", default=300, show_default=True, help="Section auto-generation interval in seconds.")
@click.option("--no-segment", is_flag=True, default=False, help="Skip ffmpeg video segmentation.")
def prepare(video: str, output: str, subtitles: str | None, interval: int, no_segment: bool) -> None:
    """Extract audio, transcribe, segment video, and generate section markers."""
    try:
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        result = process_video(video, output, no_segment=no_segment)
        audio_path = Path(result["audio"])  # type: ignore[arg-type]

        if subtitles:
            srt_src = Path(subtitles)
            srt_path = out_dir / srt_src.name
            if srt_src.resolve() != srt_path.resolve():
                shutil.copy(srt_src, srt_path)
            transcript = parse_srt(srt_path)
            click.echo(f"Using provided subtitles: {srt_path}")
        else:
            srt_path = audio_path.with_suffix(".srt")
            transcript = transcribe_to_srt(audio_path, srt_path)

        md_path = srt_path.with_suffix(".md")
        generate_markdown(transcript, md_path)
        click.echo(f"Transcript: {md_path}")

        sections = auto_generate_sections(transcript, interval)
        sections_path = out_dir / f"{out_dir.name}.sections"
        save_sections(sections, sections_path)
        click.echo(f"Sections:   {sections_path}")
        click.echo("Prepare complete. Edit the .sections file before building if desired.")

    except (FileNotFoundError, EnvironmentError, RuntimeError) as exc:
        raise click.ClickException(str(exc))


@main.command()
@click.option("--input", "input_dir", required=True, help="Directory containing prepared assets.")
@click.option("--num-questions", default=5, show_default=True, help="Number of quiz questions to generate.")
@click.option("--xlsx", is_flag=True, default=False, help="Also export quiz as an .xlsx file.")
def quiz(input_dir: str, num_questions: int, xlsx: bool) -> None:
    """Generate quiz.json from the markdown transcript.

    Uses OpenAI GPT-4o-mini when OPENAI_API_KEY is set; otherwise uses a
    built-in word-blanking fallback that requires no API key.
    """
    try:
        out_dir = Path(input_dir)
        md_files = list(out_dir.glob("*.md"))
        if not md_files:
            raise FileNotFoundError("No markdown transcript found. Run 'prepare' first.")

        questions = generate_quiz_from_transcript(str(md_files[0]), num_questions)
        quiz_path = out_dir / QUIZ_JSON_NAME
        save_quiz_to_json(questions, str(quiz_path))
        click.echo(f"Quiz:       {quiz_path}")

        if xlsx:
            xlsx_path = out_dir / "quiz.xlsx"
            save_quiz_to_xlsx(questions, str(xlsx_path))
            click.echo(f"XLSX:       {xlsx_path}")

        click.echo("Quiz complete. Run 'build' to include it in the SCORM package.")

    except (FileNotFoundError, ImportError, RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc))


@main.command()
@click.option("--video", required=True, help="Local path or HTTP(S) URL used as the video player source.")
@click.option("--input", "input_dir", required=True, help="Directory containing prepared assets.")
@click.option("--title", default="SCORM Lesson", show_default=True, help="Lesson title shown in the player.")
def build(video: str, input_dir: str, title: str) -> None:
    """Render the HTML player and SCORM manifest."""
    try:
        out_dir = Path(input_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        srt_files = list(out_dir.glob("*.srt"))
        if not srt_files:
            raise FileNotFoundError("No .srt file found in input directory. Run 'prepare' first.")

        transcript = parse_srt(srt_files[0])

        sections_path = out_dir / f"{out_dir.name}.sections"
        sections = load_sections(sections_path, transcript)
        if not sections:
            sections = auto_generate_sections(transcript, 300)
            save_sections(sections, sections_path)

        is_url = video.startswith("http://") or video.startswith("https://")
        quiz_exists = (out_dir / QUIZ_JSON_NAME).exists()

        if quiz_exists:
            generate_quiz_html(out_dir, title)
            click.echo(f"Quiz page:  {out_dir / QUIZ_HTML_NAME}")

        html_path = generate_player_html(transcript, sections, title, out_dir, video, is_url)
        manifest_path = generate_manifest(title, out_dir, include_quiz=quiz_exists)

        click.echo(f"Player:     {html_path}")
        click.echo(f"Manifest:   {manifest_path}")
        click.echo("Build complete. Run 'package' to create the SCORM zip.")

    except (FileNotFoundError, RuntimeError) as exc:
        raise click.ClickException(str(exc))


@main.command("package")
@click.option("--input", "input_dir", required=True, help="Directory containing built assets.")
@click.option("--title", default="SCORM Lesson", show_default=True, help="Lesson title (used for zip filename).")
def package_cmd(input_dir: str, title: str) -> None:
    """Bundle built assets into a SCORM-compliant zip file."""
    try:
        out_dir = Path(input_dir)
        zip_name = title.replace(" ", "_") + "_SCORM.zip"
        zip_path = out_dir / zip_name
        create_scorm_package(str(out_dir), str(zip_path))
        click.echo(f"SCORM package: {zip_path}")

    except (FileNotFoundError, NotADirectoryError) as exc:
        raise click.ClickException(str(exc))


if __name__ == "__main__":
    main()
