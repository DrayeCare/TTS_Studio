"""Offscreen integration test for the operator/stage wiring."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from PySide6.QtWidgets import QApplication, QLabel

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


def test_team_panel_and_stage_scoreboard(studio):
    studio.controller.reset()
    controller = studio.controller
    panel = studio.operator.team_panel

    panel.name_input.setText("Alpha")
    panel.add_button.click()
    panel.name_input.setText("Beta")
    panel.add_button.click()

    assert panel.team_list.count() == 2
    assert controller.state.selected_team_id == 1
    labels = [label.text() for label in studio.stage.scoreboard.findChildren(QLabel)]
    assert "ALPHA" in labels and "BETA" in labels

    panel.amount_spin.setValue(25)
    panel.reason_input.setText("Jawaban benar")
    panel.add_score_button.click()

    assert controller.state.teams[0].score == 25
    assert panel.team_list.item(0).text() == "Alpha — 25"
    assert "25" in [label.text() for label in studio.stage.scoreboard.findChildren(QLabel)]
    assert "#1 Alpha +25 → 25" in panel.history.item(0).text()
    assert "+25 poin" in panel.feedback.text()


def test_undo_button_updates_panel_and_scoreboard(studio):
    studio.controller.reset()
    controller = studio.controller
    panel = studio.operator.team_panel

    panel.name_input.setText("Alpha")
    panel.add_button.click()
    panel.amount_spin.setValue(10)
    panel.add_score_button.click()
    assert panel.undo_button.isEnabled()

    panel.undo_button.click()

    assert controller.state.teams[0].score == 0
    assert "[undo]" in panel.history.item(0).text()
    assert "Undo transaksi #1" in panel.feedback.text()
    assert not panel.undo_button.isEnabled()


def test_question_workflow_still_works_with_teams_present(studio):
    studio.controller.reset()
    controller = studio.controller
    controller.add_team("Alpha", 5)
    question_set = load_question_set(ROOT / "data" / "questions" / "sample_questions.json")

    controller.load_question_set(question_set.title, question_set.questions)
    controller.select_question(0)
    controller.show_question()
    controller.reveal_answer()

    assert "Kenapa ayam" in studio.stage.question.text()
    assert "sisi seberang" in studio.stage.answer.text()
    labels = [label.text() for label in studio.stage.scoreboard.findChildren(QLabel)]
    assert "ALPHA" in labels and "5" in labels


def test_duplicate_name_is_kept_for_correction(studio):
    studio.controller.reset()
    panel = studio.operator.team_panel

    panel.name_input.setText("Alpha")
    panel.add_button.click()
    panel.name_input.setText("alpha")
    panel.add_button.click()

    assert panel.team_list.count() == 1
    assert panel.name_input.text() == "alpha"
    assert "sudah ada" in panel.feedback.text()


def test_reset_hides_stage_scoreboard(studio):
    studio.controller.reset()
    studio.controller.add_team("Alpha", 5)
    assert not studio.stage.scoreboard.isHidden()

    studio.controller.reset()

    assert studio.stage.scoreboard.isHidden()
    assert studio.operator.team_panel.team_list.count() == 0
