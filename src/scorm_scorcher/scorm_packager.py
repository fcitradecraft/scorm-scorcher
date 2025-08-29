"""SCORM packaging utilities."""

from pathlib import Path
from zipfile import ZipFile


def create_scorm_package(source_dir: str, output_zip: str) -> None:
    """Zip the source directory into a SCORM package."""
    src = Path(source_dir)
    if not src.is_dir():
        raise NotADirectoryError(f"Source directory not found: {source_dir}")

    with ZipFile(output_zip, "w") as zf:
        for file in src.rglob("*"):
            zf.write(file, file.relative_to(src))
