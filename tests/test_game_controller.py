"""UI-independent tests for the gameplay controller."""

import pytest

from core.game_controller import GameController
from models.question import Question


@pytest.fixture
def controller():
    return GameController()


@pytest.fixture
def questions():
    return [
        Question(
            id=f"q{i}",
            number=i,
            category="Umum",
            question=f"Soal {i}?",
            answer=f"Jawaban {i}.",
        )
        for i in range(1, 4)
    ]


def observe(controller):
    seen = []
    controller.state_changed.connect(lambda state: seen.append(state))
    return seen


def test_initial_state_is_empty(controller):
    assert controller.current_question is None
    assert controller.state.questions == []
    assert not controller.state.game_started


def test_load_question_set(controller, questions):
    seen = observe(controller)
    controller.load_question_set("Babak 1", questions)

    state = controller.state
    assert state.title == "Babak 1"
    assert state.questions == questions
    assert state.current_index is None
    assert len(seen) == 1 and seen[0] is state


def test_select_question_updates_text_and_hides_reveal(controller, questions):
    controller.load_question_set("Set", questions)
    controller.select_question(1)

    assert controller.current_question == questions[1]
    assert controller.state.current_question_id == "q2"
    assert controller.state.question_text == "Soal 2?"
    assert controller.state.answer_text == "Jawaban 2."
    assert not controller.state.question_visible
    assert not controller.state.answer_visible


@pytest.mark.parametrize("index", [-1, 3, True, None, "1"])
def test_invalid_selection_is_ignored(controller, questions, index):
    controller.load_question_set("Set", questions)
    seen = observe(controller)

    assert controller.select_question(index) is False
    assert controller.state.current_index is None
    assert seen == []


def test_next_and_previous_are_bounded(controller, questions):
    controller.load_question_set("Set", questions)

    assert controller.next_question() is True
    assert controller.state.current_index == 0
    assert controller.next_question() is True
    assert controller.state.current_index == 1
    assert controller.next_question() is True
    assert controller.state.current_index == 2
    assert controller.next_question() is False
    assert controller.state.current_index == 2
    assert controller.previous_question() is True
    assert controller.state.current_index == 1
    controller.select_question(0)
    assert controller.previous_question() is False


def test_show_requires_a_selected_question(controller, questions):
    controller.load_question_set("Set", questions)
    assert controller.show_question() is False

    controller.select_question(0)
    assert controller.show_question() is True
    assert controller.state.question_visible is True


def test_answer_lifecycle(controller, questions):
    controller.load_question_set("Set", questions)
    controller.select_question(0)

    assert controller.reveal_answer() is False
    controller.show_question()
    assert controller.reveal_answer() is True
    assert controller.state.answer_visible is True
    # Repeating a reveal is harmless and keeps the state consistent.
    assert controller.reveal_answer() is True
    assert controller.state.answer_visible is True
    assert controller.hide_answer() is True
    assert controller.hide_answer() is False


def test_selecting_another_question_hides_reveal(controller, questions):
    controller.load_question_set("Set", questions)
    controller.select_question(0)
    controller.show_question()
    controller.reveal_answer()

    controller.select_question(1)
    assert not controller.state.question_visible
    assert not controller.state.answer_visible


def test_mark_completed_is_idempotent(controller, questions):
    controller.load_question_set("Set", questions)
    controller.select_question(0)

    assert controller.mark_completed() is True
    assert controller.state.completed_questions == ["q1"]
    assert controller.mark_completed() is False
    assert controller.state.completed_questions == ["q1"]


def test_game_flow_guards(controller, questions):
    assert controller.start_game() is False
    controller.load_question_set("Set", questions)

    assert controller.pause_game() is False
    assert controller.start_game() is True
    assert controller.pause_game() is True
    assert controller.pause_game() is False
    assert controller.state.game_paused is True
    assert controller.resume_game() is True
    assert controller.state.game_paused is False
    assert controller.resume_game() is False


def test_reset_keeps_state_identity_and_clears_everything(controller, questions):
    controller.load_question_set("Set", questions)
    controller.select_question(0)
    controller.show_question()
    controller.mark_completed()
    controller.start_game()
    state = controller.state
    seen = observe(controller)

    controller.reset()

    assert controller.state is state
    assert len(seen) == 1
    assert state.questions == []
    assert state.completed_questions == []
    assert state.game_started is False
    assert state.question_visible is False
    assert state.current_index is None


def test_set_question_legacy_api_matches_loaded_id(controller, questions):
    controller.load_question_set("Set", questions)

    controller.set_question("q3", "Soal manual?", "Jawaban manual.")

    assert controller.state.current_index == 2
    assert controller.state.question_text == "Soal manual?"
    assert controller.state.answer_text == "Jawaban manual."
    assert controller.show_question() is True
