"""Tests for builder.py — HTML and manifest generation."""

import json
from pathlib import Path

import pytest

from scorm_scorcher.builder import (
    BRANDING_NAME,
    QUIZ_HTML_NAME,
    QUIZ_JSON_NAME,
    generate_manifest,
    generate_player_html,
    generate_quiz_html,
)

TRANSCRIPT = [{"index": 1, "start": "00:00:01,000", "end": "00:00:03,000", "start_seconds": 1, "text": "Hello"}]
SECTIONS = [{"start": "00:00:00,000", "start_seconds": 0, "title": "Intro"}]


def test_generate_player_html_local(tmp_path):
    video = tmp_path / "lesson.mp4"
    video.write_bytes(b"")
    html = generate_player_html(TRANSCRIPT, SECTIONS, "Test", tmp_path, str(video), is_url=False)
    assert html.exists()
    content = html.read_text(encoding="utf-8")
    assert "lesson.mp4" in content
    assert "Hello" in content
    assert "Intro" in content
    assert (tmp_path / BRANDING_NAME).exists()


def test_generate_player_html_url(tmp_path):
    html = generate_player_html(
        TRANSCRIPT, SECTIONS, "Test", tmp_path,
        "https://www.youtube.com/watch?v=abc123", is_url=True,
    )
    content = html.read_text(encoding="utf-8")
    assert "youtube" in content
    assert "abc123" in content


def test_generate_quiz_html(tmp_path):
    quiz_data = {"questions": [{"type": "true_false", "prompt": "True?", "answer": True}]}
    (tmp_path / QUIZ_JSON_NAME).write_text(json.dumps(quiz_data), encoding="utf-8")
    out = generate_quiz_html(tmp_path, "My Quiz")
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "My Quiz" in content
    assert "True?" in content


def test_generate_manifest_no_quiz(tmp_path):
    manifest = generate_manifest("My Lesson", tmp_path, include_quiz=False)
    content = manifest.read_text(encoding="utf-8")
    assert "MY_LESSON_SCORM" in content
    assert "SCORM" in content
    assert QUIZ_HTML_NAME not in content


def test_generate_manifest_with_quiz(tmp_path):
    manifest = generate_manifest("My Lesson", tmp_path, include_quiz=True)
    content = manifest.read_text(encoding="utf-8")
    assert QUIZ_HTML_NAME in content
    assert "masteryscore" in content
