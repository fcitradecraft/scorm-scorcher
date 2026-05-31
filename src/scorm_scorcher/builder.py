"""HTML player and SCORM manifest generation."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List

TEMPLATE_DIR = Path(__file__).parent / "templates"
QUIZ_HTML_NAME = "quiz.html"
QUIZ_JSON_NAME = "quiz.json"
BRANDING_NAME = "branding.css"


def _video_type(video_src: str, is_url: bool) -> str:
    if not is_url:
        return "local"
    url = video_src.lower()
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "learnworlds" in url:
        return "learnworlds"
    return "url"


def generate_player_html(
    transcript: List[dict],
    sections: List[dict],
    title: str,
    output_dir: Path,
    video_src: str,
    is_url: bool,
) -> Path:
    """Render the video player HTML into output_dir/index.html."""
    template = (TEMPLATE_DIR / "player_template.html").read_text(encoding="utf-8")
    shutil.copy(TEMPLATE_DIR / BRANDING_NAME, output_dir / BRANDING_NAME)

    if is_url:
        video_value = video_src
    else:
        video_path = Path(video_src)
        dest = output_dir / video_path.name
        if video_path.resolve() != dest.resolve():
            shutil.copy(video_path, dest)
        video_value = video_path.name

    html = (
        template
        .replace("{{TRANSCRIPT_JSON}}", json.dumps(transcript))
        .replace("{{SECTIONS_JSON}}", json.dumps(sections))
        .replace("{{TITLE}}", title)
        .replace("{{VIDEO}}", video_value)
        .replace("{{VIDEO_TYPE}}", _video_type(video_src, is_url))
    )

    out = output_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def generate_quiz_html(output_dir: Path, title: str) -> Path:
    """Render the quiz player HTML into output_dir/quiz.html."""
    template = (TEMPLATE_DIR / "quiz_template.html").read_text(encoding="utf-8")
    shutil.copy(TEMPLATE_DIR / BRANDING_NAME, output_dir / BRANDING_NAME)

    quiz_json_path = output_dir / QUIZ_JSON_NAME
    quiz_data = "{}" if not quiz_json_path.exists() else quiz_json_path.read_text(encoding="utf-8")

    html = template.replace("{{TITLE}}", title).replace("{{QUIZ_DATA}}", quiz_data)
    out = output_dir / QUIZ_HTML_NAME
    out.write_text(html, encoding="utf-8")
    return out


def generate_manifest(title: str, output_dir: Path, include_quiz: bool = False) -> Path:
    """Write an imsmanifest.xml SCORM 1.2 manifest into output_dir."""
    identifier = title.replace(" ", "_").upper() + "_SCORM"

    quiz_items = ""
    quiz_resources = ""
    if include_quiz:
        quiz_items = (
            f'      <item identifier="QUIZ1" identifierref="RESQ1">\n'
            f'        <title>Quiz</title>\n'
            f'        <adlcp:masteryscore>80</adlcp:masteryscore>\n'
            f'      </item>\n'
        )
        quiz_resources = (
            f'    <resource identifier="RESQ1" type="webcontent" adlcp:scormtype="sco" href="{QUIZ_HTML_NAME}">\n'
            f'      <file href="{QUIZ_HTML_NAME}" />\n'
            f'      <file href="{QUIZ_JSON_NAME}" />\n'
            f'      <file href="{BRANDING_NAME}" />\n'
            f'    </resource>\n'
        )

    manifest = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{identifier}" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd
                      http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>{title}</title>
      <item identifier="ITEM1" identifierref="RES1">
        <title>{title}</title>
      </item>
{quiz_items}    </organization>
  </organizations>
  <resources>
    <resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html" />
      <file href="{BRANDING_NAME}" />
    </resource>
{quiz_resources}  </resources>
</manifest>"""

    out = output_dir / "imsmanifest.xml"
    out.write_text(manifest, encoding="utf-8")
    return out
