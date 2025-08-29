"""Quiz generation using OpenAI API."""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


@dataclass
class QuizQuestion:
    """Dataclass representing a quiz question."""

    question: str
    choices: List[str]
    answer: str


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

    transcript = path.read_text(encoding="utf-8")

    prompt = (
        "Create a multiple-choice quiz in JSON format. "
        f"Return {num_questions} questions with 'question', 'choices', and 'answer' fields.\n"
        "Transcript:\n" + transcript
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message["content"]
    data = json.loads(content)
    return [QuizQuestion(**item) for item in data]


def save_quiz_to_json(questions: List[QuizQuestion], output_path: str) -> None:
    """Save quiz questions to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([asdict(q) for q in questions], f, indent=2)


def save_quiz_to_xlsx(questions: List[QuizQuestion], output_path: str) -> None:
    """Save quiz questions to an XLSX file."""
    try:  # pragma: no cover - optional dependency
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "The 'pandas' package is required to export quizzes to XLSX."
        ) from exc

    df = pd.DataFrame([asdict(q) for q in questions])
    df.to_excel(output_path, index=False)
