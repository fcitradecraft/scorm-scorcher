import json
import sys
from types import SimpleNamespace

from scorm_scorcher.quiz_generation import (
    QuizQuestion,
    generate_quiz_from_markdown,
    save_quiz_to_json,
)


def _fake_openai_module(data):
    class ChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            return SimpleNamespace(
                choices=[SimpleNamespace(message={"content": json.dumps(data)})]
            )

    return SimpleNamespace(ChatCompletion=ChatCompletion)


def test_generate_quiz_from_markdown(monkeypatch, tmp_path):
    md = tmp_path / "transcript.md"
    md.write_text("content")

    data = [
        {"question": "Q1?", "choices": ["A", "B"], "answer": "A"},
        {"question": "Q2?", "choices": ["C", "D"], "answer": "D"},
    ]

    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setitem(sys.modules, "openai", _fake_openai_module(data))

    questions = generate_quiz_from_markdown(str(md), num_questions=2)

    assert len(questions) == 2
    assert questions[0].question == "Q1?"
    assert questions[0].choices == ["A", "B"]
    assert questions[0].answer == "A"


def test_save_quiz_to_json(tmp_path):
    questions = [QuizQuestion(question="Q?", choices=["A", "B"], answer="A")]
    out = tmp_path / "quiz.json"
    save_quiz_to_json(questions, str(out))

    data = json.loads(out.read_text())
    assert data == [{"question": "Q?", "choices": ["A", "B"], "answer": "A"}]
