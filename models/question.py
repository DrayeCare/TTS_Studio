"""Validated data model for a single TTS question."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: str
    number: int
    category: str
    question: str
    answer: str
    hint: str = ""
    notes: str = ""
    points: int = 0

    @classmethod
    def from_dict(cls, raw, position):
        """Build a Question from one JSON object.

        ``position`` is the 1-based index in the source file and is used in
        error messages so an operator can find the bad entry quickly.
        """
        if not isinstance(raw, dict):
            raise ValueError(f"Soal #{position} harus berupa objek JSON.")

        def text(field, required=False, default=""):
            value = raw.get(field, default)
            if value is None:
                value = ""
            if not isinstance(value, str):
                raise ValueError(f"Soal #{position}: field '{field}' harus berupa teks.")
            value = value.strip()
            if required and not value:
                raise ValueError(f"Soal #{position}: field '{field}' wajib diisi.")
            return value

        def integer(field, default=0, minimum=None):
            value = raw.get(field, default)
            if value is None or value == "":
                value = default
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(
                    f"Soal #{position}: field '{field}' harus berupa bilangan bulat."
                )
            if minimum is not None and value < minimum:
                raise ValueError(
                    f"Soal #{position}: field '{field}' harus >= {minimum}."
                )
            return value

        return cls(
            id=text("id", required=True),
            number=integer("number", default=position, minimum=1),
            category=text("category") or "Umum",
            question=text("question", required=True),
            answer=text("answer", required=True),
            hint=text("hint"),
            notes=text("notes"),
            points=integer("points", minimum=0),
        )
