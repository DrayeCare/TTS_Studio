import json

import pytest

from models.question import Question
from services.question_service import QuestionSetError, load_question_set


def write_set(tmp_path, data):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def valid_data():
    return {
        "title": "Babak 1",
        "questions": [
            {
                "id": "q001",
                "number": 1,
                "category": "Umum",
                "question": "Soal satu?",
                "answer": "Jawaban satu.",
                "hint": "Petunjuk",
                "notes": "Catatan",
                "points": 10,
            },
            {
                "id": "q002",
                "number": 2,
                "question": "Soal dua?",
                "answer": "Jawaban dua.",
            },
        ],
    }


def test_load_valid_set(tmp_path):
    result = load_question_set(write_set(tmp_path, valid_data()))

    assert result.title == "Babak 1"
    assert len(result.questions) == 2
    assert result.questions[0] == Question(
        id="q001",
        number=1,
        category="Umum",
        question="Soal satu?",
        answer="Jawaban satu.",
        hint="Petunjuk",
        notes="Catatan",
        points=10,
    )


def test_missing_optional_fields_get_safe_defaults(tmp_path):
    data = {"questions": [{"id": "a", "question": "  Q? ", "answer": " A "}]}
    result = load_question_set(write_set(tmp_path, data))
    question = result.questions[0]

    assert result.title == ""
    assert question.number == 1
    assert question.category == "Umum"
    assert question.points == 0
    assert question.question == "Q?"
    assert question.answer == "A"


def test_missing_file_reports_path(tmp_path):
    with pytest.raises(QuestionSetError, match="tidak ditemukan"):
        load_question_set(tmp_path / "nope.json")


def test_invalid_json_reports_line(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{ broken", encoding="utf-8")
    with pytest.raises(QuestionSetError, match="JSON tidak valid"):
        load_question_set(path)


def test_root_must_be_object(tmp_path):
    with pytest.raises(QuestionSetError, match="objek JSON"):
        load_question_set(write_set(tmp_path, []))


def test_questions_must_be_non_empty_list(tmp_path):
    with pytest.raises(QuestionSetError, match="tidak kosong"):
        load_question_set(write_set(tmp_path, {"questions": []}))
    with pytest.raises(QuestionSetError, match="tidak kosong"):
        load_question_set(write_set(tmp_path, {"questions": {}}))


@pytest.mark.parametrize("field", ["id", "question", "answer"])
def test_required_fields_cannot_be_blank(tmp_path, field):
    data = valid_data()
    data["questions"][0][field] = ""
    with pytest.raises(QuestionSetError, match="wajib diisi"):
        load_question_set(write_set(tmp_path, data))


def test_wrong_field_type_is_rejected(tmp_path):
    data = valid_data()
    data["questions"][0]["question"] = 42
    with pytest.raises(QuestionSetError, match="harus berupa teks"):
        load_question_set(write_set(tmp_path, data))


def test_boolean_is_not_an_integer(tmp_path):
    data = valid_data()
    data["questions"][0]["number"] = True
    with pytest.raises(QuestionSetError, match="bilangan bulat"):
        load_question_set(write_set(tmp_path, data))


def test_negative_points_rejected(tmp_path):
    data = valid_data()
    data["questions"][0]["points"] = -5
    with pytest.raises(QuestionSetError, match=">= 0"):
        load_question_set(write_set(tmp_path, data))


def test_duplicate_ids_rejected(tmp_path):
    data = valid_data()
    data["questions"][1]["id"] = "q001"
    with pytest.raises(QuestionSetError, match="duplikat"):
        load_question_set(write_set(tmp_path, data))


def test_non_object_question_entry_is_rejected(tmp_path):
    data = {"questions": ["not an object"]}
    with pytest.raises(QuestionSetError, match="objek JSON"):
        load_question_set(write_set(tmp_path, data))
