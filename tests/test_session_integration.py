"""Offscreen integration: startup restore, autosave and operator feedback."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel

from app.application import TTSStudioApplication
from core.game_controller import GameController
from models.question import Question
from services import session_service
from services.session_service import load_session, save_session

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def make_studio(tmp_path):
    app = QApplication.instance() or QApplication([])
    created = []

    def build(interval_ms=10):
        studio = TTSStudioApplication(
            session_path=tmp_path / "session.json", autosave_ms=interval_ms
        )
        created.append(studio)
        return studio

    yield build, tmp_path / "session.json"

    for studio in created:
        studio.autosave.flush()


def rich_state():
    controller = GameController()
    controller.load_question_set(
        "Babak 1",
        [
            Question(id="q1", number=1, category="Umum", question="Q1?", answer="A1"),
            Question(id="q2", number=2, category="Sulit", question="Q2?", answer="A2"),
        ],
    )
    controller.select_question(1)
    controller.show_question()
    controller.reveal_answer()
    controller.add_team("Alpha", 10)
    controller.add_team("Beta", 20)
    controller.adjust_score(1, 25, "Benar")
    controller.undo_last_score()
    return controller.state


def test_fresh_startup_reports_no_session(make_studio):
    build, _ = make_studio
    studio = build()

    assert studio.session_result.source == "none"
    assert "baru" in studio.operator.session_status.text().lower()
    assert studio.operator.question_list.count() == 0


def test_startup_restores_questions_teams_and_windows(make_studio):
    build, path = make_studio
    save_session(path, rich_state())

    studio = build()

    assert studio.session_result.source == "primary"
    assert studio.operator.question_list.count() == 2
    assert studio.operator.question_list.currentRow() == 1
    assert "Q2?" in studio.stage.question.text()
    assert "A2" in studio.stage.answer.text()
    labels = [label.text() for label in studio.stage.scoreboard.findChildren(QLabel)]
    assert "ALPHA" in labels and "BETA" in labels and "10" in labels and "20" in labels
    assert studio.operator.team_panel.team_list.count() == 2
    assert "dipulihkan" in studio.operator.session_status.text().lower()
    assert studio.operator.team_panel.history.count() == 2


def test_autosave_coalesces_and_writes_after_change(make_studio):
    build, path = make_studio
    studio = build(interval_ms=10)

    studio.controller.load_question_set(
        "Set", [Question(id="q1", number=1, category="Umum", question="Q?", answer="A")]
    )
    studio.controller.add_team("Alpha", 5)
    assert not path.exists()  # debounce has not fired yet

    QTest.qWait(150)

    assert path.exists()
    result = load_session(path)
    assert result.state.title == "Set"
    assert [team.name for team in result.state.teams] == ["Alpha"]
    assert "tersimpan" in studio.operator.session_status.text().lower()


def test_flush_writes_immediately_and_skips_redundant_writes(make_studio):
    build, path = make_studio
    studio = build()

    studio.controller.add_team("Alpha", 5)
    studio.autosave.flush()
    assert path.exists()
    first = path.read_bytes()
    studio.autosave.flush()

    assert path.read_bytes() == first


def test_reset_is_persisted(make_studio):
    build, path = make_studio
    studio = build()
    studio.controller.add_team("Alpha", 25)
    studio.autosave.flush()
    assert load_session(path).state.teams[0].score == 25

    studio.controller.reset()
    studio.autosave.flush()

    restored = load_session(path).state
    assert restored.teams == []
    assert restored.questions == []
    assert restored.score_history == []


def test_write_failure_is_visible_without_modal_dialog(make_studio, monkeypatch):
    build, path = make_studio
    studio = build()
    studio.controller.add_team("Alpha", 5)
    studio.autosave.flush()

    def denied(source, target):
        raise OSError("akses ditolak")

    monkeypatch.setattr(session_service.os, "replace", denied)

    studio.controller.adjust_score(1, 10, "Benar")
    studio.autosave.flush()

    assert "Gagal menyimpan" in studio.operator.session_status.text()
    assert "akses ditolak" in studio.operator.session_status.text()


def test_new_session_archives_recoverable_state(make_studio):
    build, path = make_studio
    studio = build()
    studio.controller.add_team("Alpha", 42)
    studio.autosave.flush()

    studio.operator.new_session_requested.emit()

    archives = list(path.parent.glob("session.previous-*.json"))
    assert len(archives) == 1
    assert load_session(archives[0]).state.teams[0].score == 42
    assert studio.controller.state.teams == []


def test_backup_recovery_is_reported_in_operator_status(make_studio):
    build, path = make_studio
    save_session(path, rich_state())
    backup = path.with_name("session.backup.json")
    original = path.read_bytes()
    save_session(path, GameController().state)
    path.write_bytes(original)
    path.write_text("{ rusak", encoding="utf-8")
    assert backup.exists()

    studio = build()

    assert studio.session_result.source == "backup"
    assert "cadangan" in studio.operator.session_status.text().lower()
    assert studio.operator.question_list.count() == 2


def test_question_workflow_still_functional_after_restore(make_studio):
    build, path = make_studio
    save_session(path, rich_state())
    studio = build()

    studio.controller.hide_answer()
    studio.controller.next_question()
    studio.controller.previous_question()

    studio.controller.show_question()
    assert studio.controller.state.current_index == 0
    assert studio.stage.answer.text() == ""
    assert "Q1?" in studio.stage.question.text()
