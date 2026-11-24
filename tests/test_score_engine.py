"""Pure scoring-ledger rules."""

from datetime import datetime

import pytest

from core.score_engine import (
    DEFAULT_REASON,
    MAX_REASON_LENGTH,
    build_undo,
    mark_undone,
    new_transaction,
    validate_amount,
    validate_reason,
)


@pytest.mark.parametrize("amount", [1, -1, 100, -9999])
def test_valid_amounts_pass_through(amount):
    assert validate_amount(amount) == amount


@pytest.mark.parametrize("amount", [0, True, False, "5", 1.5, None])
def test_invalid_amounts_raise(amount):
    with pytest.raises(ValueError):
        validate_amount(amount)


def test_reason_defaults_and_is_normalized():
    assert validate_reason("") == DEFAULT_REASON
    assert validate_reason(None) == DEFAULT_REASON
    assert validate_reason("  jawaban   benar  ") == "jawaban benar"
    with pytest.raises(ValueError):
        validate_reason("x" * (MAX_REASON_LENGTH + 1))
    with pytest.raises(ValueError):
        validate_reason(42)


def test_transaction_records_all_required_fields():
    transaction = new_transaction(3, 7, "Alpha", -10, "Penalti", 15)

    assert transaction.sequence == 3
    assert transaction.team_id == 7
    assert transaction.team_name == "Alpha"
    assert transaction.amount == -10
    assert transaction.reason == "Penalti"
    assert transaction.resulting_score == 15
    assert transaction.kind == "score"
    assert transaction.undone is False
    assert datetime.fromisoformat(transaction.timestamp).tzinfo is not None


def test_undo_entry_mirrors_amount_and_links_to_original():
    original = new_transaction(1, 2, "Beta", 25, "Benar", 45, timestamp="T1")

    undo = build_undo(original, current_score=30, sequence=2, timestamp="T2")

    assert undo.amount == -25
    assert undo.resulting_score == 5
    assert undo.team_id == 2
    assert undo.team_name == "Beta"
    assert undo.reason == "Undo #1"
    assert undo.kind == "undo"
    assert undo.reverses == 1
    assert undo.timestamp == "T2"
    assert original.amount == 25  # original is immutable


def test_mark_undone_returns_a_copy():
    original = new_transaction(1, 2, "Beta", 25, "Benar", 25)

    marked = mark_undone(original)

    assert marked.undone is True
    assert original.undone is False
