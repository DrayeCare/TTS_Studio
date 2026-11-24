"""Controller-level scoring and undo rules."""

from datetime import datetime

import pytest

from core.game_controller import GameController

INITIAL_SCORES = {1: 10, 2: 20}


@pytest.fixture
def game():
    controller = GameController()
    controller.add_team("Alpha", INITIAL_SCORES[1])
    controller.add_team("Beta", INITIAL_SCORES[2])
    return controller


def observe(controller):
    seen = []
    controller.state_changed.connect(lambda state: seen.append(state))
    return seen


def ledger_score(team_id, history):
    """Score implied by the append-only ledger (initial + every entry)."""
    return INITIAL_SCORES[team_id] + sum(
        transaction.amount
        for transaction in history
        if transaction.team_id == team_id
    )


def test_add_and_subtract_record_complete_transactions(game):
    game.adjust_score(1, 15, "Jawaban benar")
    game.adjust_score(2, -7, "Penalti")

    assert [team.score for team in game.state.teams] == [25, 13]

    first, second = game.state.score_history
    assert (first.sequence, first.team_id, first.team_name) == (1, 1, "Alpha")
    assert (first.amount, first.reason, first.resulting_score) == (
        15, "Jawaban benar", 25
    )
    assert datetime.fromisoformat(first.timestamp).tzinfo is not None
    assert (second.sequence, second.team_name, second.amount) == (2, "Beta", -7)
    assert game.state.next_transaction_id == 3


def test_resulting_score_may_be_negative(game):
    assert game.adjust_score(1, -50, "Penalti besar") is True
    assert game.state.teams[0].score == -40
    assert game.state.score_history[0].resulting_score == -40


@pytest.mark.parametrize("amount", [0, True, False, "5", 1.5, None])
def test_invalid_amounts_are_atomic(game, amount):
    before_scores = [team.score for team in game.state.teams]
    before_history = list(game.state.score_history)

    assert game.adjust_score(1, amount) is False
    assert [team.score for team in game.state.teams] == before_scores
    assert game.state.score_history == before_history
    assert game.state.next_transaction_id == 1
    assert "Jumlah poin" in game.state.last_action


def test_unknown_team_and_bool_id_are_rejected(game):
    assert game.adjust_score(99, 10) is False
    assert game.adjust_score(True, 10) is False
    assert game.state.score_history == []
    assert [team.score for team in game.state.teams] == [10, 20]


def test_long_reason_is_rejected_atomically(game):
    assert game.adjust_score(1, 5, "x" * 200) is False
    assert game.state.score_history == []
    assert game.state.teams[0].score == 10


def test_history_stays_consistent_across_many_transactions(game):
    game.adjust_score(1, 10, "a")
    game.adjust_score(1, -5, "b")
    game.adjust_score(2, 7, "c")
    game.adjust_score(2, -2, "d")

    assert game.state.next_transaction_id == 5
    for team in game.state.teams:
        assert team.score == ledger_score(team.id, game.state.score_history)


def test_undo_reverses_last_transaction_and_keeps_audit_trail(game):
    game.adjust_score(1, 10, "Benar")

    assert game.undo_last_score() is True
    assert game.state.teams[0].score == 10
    assert len(game.state.score_history) == 2

    original, undo = game.state.score_history
    assert original.undone is True
    assert undo.kind == "undo"
    assert undo.reverses == 1
    assert undo.amount == -10
    assert undo.resulting_score == 10
    assert "Undo transaksi #1" in game.state.last_action
    assert game.state.teams[0].score == ledger_score(1, game.state.score_history)


def test_repeated_undo_walks_back_through_transactions(game):
    game.adjust_score(1, 10)
    game.adjust_score(1, 5)
    game.adjust_score(2, 7)

    assert game.undo_last_score() is True
    assert [team.score for team in game.state.teams] == [25, 20]
    assert game.undo_last_score() is True
    assert [team.score for team in game.state.teams] == [20, 20]
    assert game.undo_last_score() is True
    assert [team.score for team in game.state.teams] == [10, 20]

    assert game.undo_last_score() is False
    assert "Tidak ada transaksi" in game.state.last_action
    assert len(game.state.score_history) == 6
    for team in game.state.teams:
        assert team.score == ledger_score(team.id, game.state.score_history)


def test_undo_does_not_modify_unrelated_state(game):
    game.set_question("q1", "Soal?", "Jawaban")
    game.show_question()
    game.mark_completed()
    game.select_team(2)
    game.adjust_score(1, 10, "Benar")

    before = (
        game.state.question_text,
        game.state.question_visible,
        list(game.state.completed_questions),
        game.state.selected_team_id,
        game.state.teams[1].score,
        game.state.next_team_id,
    )

    assert game.undo_last_score() is True

    assert (
        game.state.question_text,
        game.state.question_visible,
        list(game.state.completed_questions),
        game.state.selected_team_id,
        game.state.teams[1].score,
        game.state.next_team_id,
    ) == before


def test_undo_refuses_transaction_for_removed_team(game):
    game.add_team("Gamma", 5)
    game.adjust_score(3, 9, "Benar")
    game.remove_team(3)

    assert game.undo_last_score() is False
    assert game.state.score_history[0].undone is False
    assert len(game.state.score_history) == 1
    assert [team.score for team in game.state.teams] == [10, 20]


def test_rename_does_not_rewrite_audit_names(game):
    game.adjust_score(1, 5, "Benar")
    game.rename_team(1, "Alpha Baru")

    assert game.state.teams[0].name == "Alpha Baru"
    assert game.state.score_history[0].team_name == "Alpha"


def test_each_mutation_emits_once(game):
    seen = observe(game)

    game.adjust_score(1, 5)
    game.undo_last_score()
    game.adjust_score(1, 0)

    assert seen == [game.state, game.state, game.state]


def test_reset_clears_ledger_in_place(game):
    game.adjust_score(1, 10)
    state = game.state

    game.reset()

    assert game.state is state
    assert state.score_history == []
    assert state.next_transaction_id == 1
    assert state.teams == []
