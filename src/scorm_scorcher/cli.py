"""Command line interface for the project."""

from pathlib import Path

import click

from .video_processing import process_video
from .scorm_packager import create_scorm_package


@click.command()
@click.argument("video_path", type=click.Path(dir_okay=False), metavar="VIDEO_PATH")
@click.option(
    "--output-dir",
    default="output/",
    show_default=True,
    help="Directory where the SCORM package will be created.",
)
def main(video_path: str, output_dir: str) -> None:
    """Convert VIDEO_PATH into a SCORM package."""

    try:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        process_video(video_path, str(out_dir))
        output_zip = out_dir / "scorm_package.zip"
        create_scorm_package(str(out_dir), str(output_zip))
        click.echo(f"Created SCORM package at {output_zip}")
    except (FileNotFoundError, NotADirectoryError, EnvironmentError, RuntimeError) as exc:
        raise click.ClickException(str(exc))


if __name__ == "__main__":
    main()
