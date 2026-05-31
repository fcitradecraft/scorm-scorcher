"""Quiz generation — OpenAI (primary) with a naive transcript-based fallback.

When OPENAI_API_KEY is set, questions are generated via GPT-4o-mini.
Without an API key the tool falls back to a simple word-blanking heuristic
derived from transcript lines, which is always available with no extra deps.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class QuizQuestion:
    type: str
    prompt: str
    answer: Any
    options: Optional[List[str]] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": self.type, "prompt": self.prompt, "answer": self.answer}
        if self.options is not None:
            d["options"] = self.options
        return d


def generate_quiz_from_transcript(
    md_path: str, num_questions: int = 5, use_openai: bool = True
) -> List[QuizQuestion]:
    """Generate quiz questions from a markdown transcript file.

    Uses the OpenAI API when OPENAI_API_KEY is in the environment and
    ``use_openai`` is True.  Falls back to the naive heuristic otherwise.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if use_openai and api_key:
        return _generate_openai(md_path, num_questions, api_key)
    return _generate_naive(md_path, num_questions)


def _generate_openai(md_path: str, num_questions: int, api_key: str) -> List[QuizQuestion]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "The 'openai' package is required for AI quiz generation. "
            "Install with: pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)
    transcript = Path(md_path).read_text(encoding="utf-8")

    prompt = (
        f"Create a {num_questions}-question multiple-choice quiz from this transcript.\n"
        "Return a JSON array. Each item must have exactly these keys:\n"
        '  {"type": "multiple_choice", "prompt": "...", "options": ["A","B","C","D"], "answer": "A"}\n'
        "Return only valid JSON — no markdown fences, no extra text.\n\n"
        "Transcript:\n" + transcript
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content.strip()
    # Strip markdown fences if the model adds them anyway
    content = re.sub(r"^```[a-z]*\n?", "", content)
    content = re.sub(r"\n?```$", "", content)

    data = json.loads(content)
    return [
        QuizQuestion(
            type=item.get("type", "multiple_choice"),
            prompt=item["prompt"],
            options=item.get("options"),
            answer=item["answer"],
        )
        for item in data
    ]


def _generate_naive(md_path: str, limit: int) -> List[QuizQuestion]:
    """Word-blanking heuristic — no external dependencies required."""
    lines = [
        line.strip()
        for line in Path(md_path).read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("-")
    ]

    questions: List[QuizQuestion] = []
    for line in lines[:limit]:
        text = line.split("]", 1)[1].strip() if "]" in line else line[1:].strip()
        words = text.split()

        if len(words) > 5:
            idx = min(2, len(words) - 1)
            answer = words[idx]
            prompt_words = words.copy()
            prompt_words[idx] = "____"
            options = [answer]
            for w in words:
                if w.lower() != answer.lower() and w not in options:
                    options.append(w)
                    if len(options) >= 4:
                        break
            questions.append(QuizQuestion(
                type="multiple_choice",
                prompt="Fill in the blank: " + " ".join(prompt_words),
                options=options,
                answer=answer,
            ))
        else:
            questions.append(QuizQuestion(
                type="true_false",
                prompt=f"True or False: {text}",
                answer=True,
            ))

    return questions


def save_quiz_to_json(questions: List[QuizQuestion], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"questions": [q.to_dict() for q in questions]}, f, indent=2)


def save_quiz_to_xlsx(questions: List[QuizQuestion], output_path: str) -> None:
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "The 'pandas' and 'openpyxl' packages are required for XLSX export. "
            "Install with: pip install pandas openpyxl"
        ) from exc
    pd.DataFrame([q.to_dict() for q in questions]).to_excel(output_path, index=False)
