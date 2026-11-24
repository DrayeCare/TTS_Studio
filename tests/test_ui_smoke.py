"""Offscreen integration test for the operator/stage wiring."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from PySide6.QtWidgets import QApplication

from app.application import TTSStudioApplication
from models.question import Question
from services.question_service import load_question_set

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def studio():
    app = QApplication.instance() or QApplication([])
    assert app is not None
    return TTSStudioApplication()


def test_sample_set_is_loadable_and_rendered(studio):
    question_set = load_question_set(ROOT / "data" / "questions" / "sample_questions.json")
    studio.controller.load_question_set(question_set.title, question_set.questions)

    assert studio.operator.question_list.count() == 1
    assert question_set.title in studio.operator.status.text()

    studio.controller.select_question(0)
    studio.controller.show_question()
    assert "Kenapa ayam" in studio.stage.question.text()

    studio.controller.reveal_answer()
    assert "sisi seberang" in studio.stage.answer.text()
    assert "••••••" not in studio.operator.detail.toPlainText()


def test_list_selection_drives_controller_and_stage(studio):
    studio.controller.load_question_set(
        "Uji",
        [
            Question(id=f"q{i}", number=i, category="Umum", question=f"Soal {i}?", answer=f"Jawaban {i}.")
            for i in range(1, 4)
        ],
    )
    assert studio.operator.question_list.count() == 3

    studio.operator.question_list.setCurrentRow(1)
    assert studio.controller.state.current_index == 1
    assert "Soal 2?" in studio.operator.detail.toPlainText()

    studio.controller.show_question()
    studio.controller.reveal_answer()
    assert "Jawaban 2." in studio.stage.answer.text()

    studio.controller.select_question(2)
    assert studio.operator.question_list.currentRow() == 2
    assert studio.stage.answer.text() == ""


def test_reset_restores_idle_screens(studio):
    studio.controller.reset()

    assert studio.operator.question_list.count() == 0
    assert studio.stage.question.text() == "TTS STUDIO"
    assert studio.stage.answer.text() == ""
    assert studio.stage.status.text() == ""
