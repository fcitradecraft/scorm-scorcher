"""Command line interface for :mod:`scorm_scorcher`.

The CLI is intentionally tiny at this stage: it accepts a path to a video
file and emits a couple of artefacts in an output directory.  As the project
evolves additional options will be added for quiz generation, SCORM
packaging and more.
"""

import click

from .video_processing import process_video


@click.command()
@click.argument("video_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output-dir",
    default="output",
    show_default=True,
    type=click.Path(file_okay=False),
    help="Directory where generated files are stored.",
)
def main(video_path: str, output_dir: str) -> None:
    """Convert ``VIDEO_PATH`` into SCORM-friendly artefacts."""

    paths = process_video(video_path, output_dir)
    for name, path in paths.items():
        click.echo(f"Created {name}: {path}")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
