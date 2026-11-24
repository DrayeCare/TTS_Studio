"""Load and validate question sets from JSON files.

The service is UI-independent: it returns plain dataclasses and raises a
single, descriptive exception type that the operator UI can display directly.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from models.question import Question


class QuestionSetError(ValueError):
    """Raised when a question set cannot be read or fails validation."""


@dataclass(frozen=True)
class QuestionSet:
    title: str
    questions: list[Question]


def load_question_set(path) -> QuestionSet:
    """Read ``path`` and return a validated QuestionSet.

    Raises QuestionSetError with an operator-readable Indonesian message for
    every expected failure mode (missing file, bad JSON, bad schema).
    """
    file_path = Path(path)
    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise QuestionSetError(f"File tidak ditemukan: {file_path}") from None
    except OSError as exc:
        raise QuestionSetError(f"Gagal membaca file: {exc}") from exc

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise QuestionSetError(
            f"JSON tidak valid (baris {exc.lineno}, kolom {exc.colno})."
        ) from exc

    if not isinstance(data, dict):
        raise QuestionSetError("Isi file harus berupa objek JSON.")

    title = data.get("title", "")
    if not isinstance(title, str):
        raise QuestionSetError("Field 'title' harus berupa teks.")

    entries = data.get("questions")
    if not isinstance(entries, list) or not entries:
        raise QuestionSetError("Field 'questions' harus berupa daftar soal yang tidak kosong.")

    questions = []
    seen_ids = set()
    for position, entry in enumerate(entries, start=1):
        try:
            question = Question.from_dict(entry, position)
        except ValueError as exc:
            raise QuestionSetError(str(exc)) from exc
        if question.id in seen_ids:
            raise QuestionSetError(
                f"ID soal duplikat: '{question.id}' (soal #{position})."
            )
        seen_ids.add(question.id)
        questions.append(question)

    return QuestionSet(title=title.strip(), questions=questions)
