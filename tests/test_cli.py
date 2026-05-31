"""Tests for the Click CLI."""

import json
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from scorm_scorcher.cli import main

SRT = textwrap.dedent("""\
    1
    00:00:01,000 --> 00:00:03,000
    Hello world

    2
    00:00:04,000 --> 00:00:06,000
    Goodbye world

""")


def _make_prepared_dir(tmp_path: Path) -> Path:
    out = tmp_path / "lesson"
    out.mkdir()
    (out / "audio.srt").write_text(SRT, encoding="utf-8")
    return out


def test_quiz_command(tmp_path):
    out = _make_prepared_dir(tmp_path)
    md = out / "audio.md"
    md.write_text("- [00:00:01,000] The quick brown fox jumps over the lazy dog\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["quiz", "--input", str(out), "--num-questions", "1"])
    assert result.exit_code == 0, result.output
    assert (out / "quiz.json").exists()
    data = json.loads((out / "quiz.json").read_text())
    assert "questions" in data


def test_build_command_local(tmp_path):
    out = _make_prepared_dir(tmp_path)
    video = tmp_path / "lesson.mp4"
    video.write_bytes(b"")

    runner = CliRunner()
    result = runner.invoke(main, [
        "build",
        "--video", str(video),
        "--input", str(out),
        "--title", "Test Lesson",
    ])
    assert result.exit_code == 0, result.output
    assert (out / "index.html").exists()
    assert (out / "imsmanifest.xml").exists()


def test_build_command_url(tmp_path):
    out = _make_prepared_dir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, [
        "build",
        "--video", "https://www.youtube.com/watch?v=test123",
        "--input", str(out),
        "--title", "Test Lesson",
    ])
    assert result.exit_code == 0, result.output
    content = (out / "index.html").read_text(encoding="utf-8")
    assert "test123" in content


def test_package_command(tmp_path):
    out = _make_prepared_dir(tmp_path)
    video = tmp_path / "lesson.mp4"
    video.write_bytes(b"")

    runner = CliRunner()
    runner.invoke(main, ["build", "--video", str(video), "--input", str(out), "--title", "My Lesson"])
    result = runner.invoke(main, ["package", "--input", str(out), "--title", "My Lesson"])
    assert result.exit_code == 0, result.output
    assert (out / "My_Lesson_SCORM.zip").exists()


def test_build_missing_srt_fails(tmp_path):
    out = tmp_path / "empty"
    out.mkdir()
    runner = CliRunner()
    result = runner.invoke(main, ["build", "--video", "x.mp4", "--input", str(out)])
    assert result.exit_code != 0
    assert "prepare" in result.output.lower() or "srt" in result.output.lower()
