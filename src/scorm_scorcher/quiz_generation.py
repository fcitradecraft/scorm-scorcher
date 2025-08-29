"""Quiz generation using OpenAI API."""

import json
import os
from pathlib import Path
from typing import List, Dict


class QuizQuestion(Dict[str, str]):
    """Dictionary subclass representing a quiz question."""


def generate_quiz_from_markdown(md_path: str, num_questions: int = 5) -> List[QuizQuestion]:
    """Placeholder for quiz generation.

    Args:
        md_path: Path to the markdown file containing transcript.
        num_questions: Number of quiz questions to generate.
    """
    try:
        import openai
    except ImportError as exc:
        raise ImportError(
            "The 'openai' package is required to generate quizzes. "
            "Install it with 'pip install openai'."
        ) from exc

    api_key = os.getenv("OPENAI_API_KEY") or getattr(openai, "api_key", None)
    if not api_key:
        raise ValueError(
            "OpenAI API key is missing. Set the OPENAI_API_KEY environment variable."
        )

    path = Path(md_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # TODO: Implement call to OpenAI API to generate quiz questions
    return []


def save_quiz_to_json(questions: List[QuizQuestion], output_path: str) -> None:
    """Save quiz questions to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
