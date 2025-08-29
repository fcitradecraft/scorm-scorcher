"""Video processing utilities."""

from pathlib import Path

def process_video(video_path: str) -> None:
    """Placeholder function for processing the video.

    Args:
        video_path: Path to the input video file.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    # TODO: implement segmentation, subtitle generation, etc.
    print(f"Processing video: {video_path}")
