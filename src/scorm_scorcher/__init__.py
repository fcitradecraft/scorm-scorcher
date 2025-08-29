"""Top-level package for ``scorm_scorcher``.

This module exposes high-level APIs for convenience and defines the
package's version.
"""

__version__ = "0.1.0"

from .video_processing import process_video
from .scorm_packager import create_scorm_package

__all__ = ["process_video", "create_scorm_package", "__version__"]

# Optional imports that require extra dependencies
try:  # pragma: no cover - optional feature
    from .quiz_generation import generate_quiz_from_markdown, save_quiz_to_json
except Exception:  # ModuleNotFoundError if optional deps missing
    pass
else:
    __all__ += ["generate_quiz_from_markdown", "save_quiz_to_json"]
