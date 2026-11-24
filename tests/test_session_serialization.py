"""Session schema, round-trip and strict validation tests."""

import pytest

from core.game_controller import GameController
from core.score_engine import ScoreTransaction
from models.question import Question
from services.session_service import (
    SESSION_VERSION,
    SessionError,
    deserialize_session,
    serialize_session,
)


def rich_state():
    controller = GameController()
    controller.load_question_set(
        "Babak 1",
        [
            Question(id="q1", number=1, category="Umum", question="Q1?", answer="A1", points=10),
            Question(id="q2", number=2, category="Sulit", question="Q2?", answer="A2", points=20),
        ],
    )
    controller.select_question(1)
    controller.show_question()
    controller.reveal_answer()
    controller.mark_completed()
    controller.start_game()
    controller.pause_game()
    controller.add_team("Alpha", 10)
    controller.add_team("Beta", 20)
    controller.select_team(2)
    controller.adjust_score(1, 25, "Benar")
    controller.adjust_score(2, -5, "Penalti")
    controller.undo_last_score()
    return controller.state


def payload(state=None):
    return serialize_session(state or rich_state())


def invalid(mutator):
    data = payload()
    mutator(data)
    with pytest.raises(SessionError):
        deserialize_session(data)


def test_payload_carries_explicit_schema_version():
    assert payload()["schema_version"] == SESSION_VERSION


@pytest.mark.parametrize(
    "field_name",
    [
        "title", "questions", "current_question_id", "current_index",
        "question_text", "answer_text", "question_visible", "answer_visible",
        "game_started", "game_paused", "completed_questions", "teams",
        "selected_team_id", "next_team_id", "score_history", "next_transaction_id",
    ],
)
def test_round_trip_preserves_field(field_name):
    state = rich_state()
    restored = deserialize_session(payload(state))

    assert getattr(restored, field_name) == getattr(state, field_name)


def test_questions_with_metadata_are_restored():
    restored = deserialize_session(payload())

    assert [question.id for question in restored.questions] == ["q1", "q2"]
    assert restored.questions[1].category == "Sulit"
    assert restored.questions[1].points == 20


def test_teams_and_scores_are_restored():
    restored = deserialize_session(payload())

    assert [(team.id, team.name, team.score) for team in restored.teams] == [
        (1, "Alpha", 35), (2, "Beta", 20)
    ]
    assert restored.selected_team_id == 2


def test_ledger_and_undo_state_are_restored():
    restored = deserialize_session(payload())

    assert [tx.kind for tx in restored.score_history] == ["score", "score", "undo"]
    assert restored.score_history[1].undone is True
    assert restored.score_history[2].reverses == 2
    assert restored.score_history[2].amount == 5
    assert restored.next_transaction_id == 4


def test_manual_question_text_is_not_reconstructed_from_set():
    state = rich_state()
    state.question_text = "Teks manual"
    state.answer_text = "Jawaban manual"

    restored = deserialize_session(payload(state))

    assert restored.question_text == "Teks manual"
    assert restored.answer_text == "Jawaban manual"


def test_empty_fresh_state_round_trips():
    fresh = GameController().state

    restored = deserialize_session(payload(fresh))

    assert restored.questions == []
    assert restored.teams == []
    assert restored.score_history == []
    assert restored.current_index is None


@pytest.mark.parametrize("version", [None, "1", True, 0, 2])
def test_invalid_or_unsupported_version_rejected(version):
    invalid(lambda data: data.update(schema_version=version))


def test_root_must_be_an_object():
    with pytest.raises(SessionError):
        deserialize_session([])


def test_duplicate_question_ids_rejected():
    invalid(lambda data: data["questions"][1].update(id="q1"))


def test_bad_question_field_rejected():
    invalid(lambda data: data["questions"][0].update(question=42))


@pytest.mark.parametrize("index", [True, 99, -1, "1"])
def test_invalid_current_index_rejected(index):
    invalid(lambda data: data.update(current_index=index))


def test_current_id_must_match_index():
    invalid(lambda data: data.update(current_question_id="q1"))


def test_current_id_without_index_rejected():
    invalid(lambda data: data.update(current_question_id="q1", current_index=None))


def test_unknown_completed_question_rejected():
    invalid(lambda data: data["completed_questions"].append("q_missing"))


def test_duplicate_completed_question_rejected():
    invalid(lambda data: data["completed_questions"].append("q2"))


def test_duplicate_team_id_rejected():
    invalid(lambda data: data["teams"][1].update(id=1))


def test_duplicate_team_name_is_case_insensitive():
    invalid(lambda data: data["teams"][1].update(name="ALPHA"))


def test_blank_team_name_rejected():
    invalid(lambda data: data["teams"][0].update(name="   "))


def test_boolean_team_score_rejected():
    invalid(lambda data: data["teams"][0].update(score=True))


def test_too_many_teams_rejected():
    def mutate(data):
        data["teams"] = [
            {"id": i, "name": f"T{i}", "score": 0} for i in range(1, 14)
        ]
        data["next_team_id"] = 14
        data["selected_team_id"] = 1
        data["score_history"] = []
        data["next_transaction_id"] = 1

    invalid(mutate)


def test_next_team_id_must_exceed_existing_ids():
    invalid(lambda data: data.update(next_team_id=1))


def test_invalid_selected_team_rejected():
    invalid(lambda data: data.update(selected_team_id=99))


def test_duplicate_transaction_sequence_rejected():
    invalid(lambda data: data["score_history"][1].update(sequence=1))


def test_decreasing_transaction_sequence_rejected():
    invalid(lambda data: data["score_history"][1].update(sequence=0))


def test_future_team_reference_in_ledger_rejected():
    invalid(lambda data: data["score_history"][0].update(team_id=99))


def test_zero_amount_in_ledger_rejected():
    invalid(lambda data: data["score_history"][0].update(amount=0))


def test_unknown_transaction_kind_rejected():
    invalid(lambda data: data["score_history"][0].update(kind="bonus"))


def test_naive_timestamp_rejected():
    invalid(lambda data: data["score_history"][0].update(timestamp="2026-01-01T00:00:00"))


def test_garbage_timestamp_rejected():
    invalid(lambda data: data["score_history"][0].update(timestamp="kemarin"))


def test_undo_must_reference_an_existing_transaction():
    invalid(lambda data: data["score_history"][2].update(reverses=99))


def test_undo_amount_must_mirror_original():
    invalid(lambda data: data["score_history"][2].update(amount=-1))


def test_original_without_undo_flag_rejected():
    invalid(lambda data: data["score_history"][1].update(undone=False))


def test_score_flagged_undone_without_undo_rejected():
    invalid(lambda data: data["score_history"][0].update(undone=True))


def test_ledger_chain_inconsistency_rejected():
    invalid(lambda data: data["score_history"][0].update(resulting_score=99))


def test_team_score_disagreeing_with_ledger_rejected():
    invalid(lambda data: data["teams"][0].update(score=999))


def test_next_transaction_id_must_match_ledger():
    invalid(lambda data: data.update(next_transaction_id=99))


def test_bool_field_rejected():
    invalid(lambda data: data.update(game_paused="ya"))


def test_boolean_field_type_is_strict():
    state = rich_state()
    data = payload(state)
    data["game_paused"] = 1
    with pytest.raises(SessionError, match="boolean"):
        deserialize_session(data)


def test_transaction_helpers_are_frozen_after_restore():
    restored = deserialize_session(payload())
    transaction = restored.score_history[0]

    assert isinstance(transaction, ScoreTransaction)
    with pytest.raises(Exception):
        transaction.amount = 99


def test_mutating_payload_does_not_change_source_state():
    state = rich_state()
    data = payload(state)
    data["teams"][0]["score"] = 9999

    assert state.teams[0].score == 35
