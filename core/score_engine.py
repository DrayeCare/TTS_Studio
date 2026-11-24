"""Pure, append-only scoring ledger. No Qt and no widget imports.

Policy (documented for operators):
- A score amount must be a non-zero integer; negative results are ALLOWED so
  a penalty can push a team below zero.
- Every mutation is one ScoreTransaction with team, amount, reason, UTC
  timestamp and the resulting score.
- Undo never deletes a transaction. It records a compensating transaction and
  flags the original as undone, so the audit trail stays complete.
- Redo is deliberately not implemented: the same effect can be achieved by
  entering the transaction again, and a second undo stack adds complexity
  without value for a live operator.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timezone

MAX_REASON_LENGTH = 80
DEFAULT_REASON = "Penyesuaian manual"


@dataclass(frozen=True)
class ScoreTransaction:
    sequence: int
    team_id: int
    team_name: str
    amount: int
    reason: str
    timestamp: str
    resulting_score: int
    kind: str = "score"          # "score" or "undo"
    reverses: int | None = None  # sequence of the transaction an undo cancels
    undone: bool = False


def validate_amount(amount) -> int:
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("Jumlah poin harus berupa bilangan bulat.")
    if amount == 0:
        raise ValueError("Jumlah poin tidak boleh nol.")
    return amount


def validate_reason(reason) -> str:
    if reason is None:
        reason = ""
    if not isinstance(reason, str):
        raise ValueError("Alasan harus berupa teks.")
    cleaned = " ".join(reason.split())
    if len(cleaned) > MAX_REASON_LENGTH:
        raise ValueError(f"Alasan maksimal {MAX_REASON_LENGTH} karakter.")
    return cleaned or DEFAULT_REASON


def new_transaction(
    sequence,
    team_id,
    team_name,
    amount,
    reason,
    resulting_score,
    kind="score",
    reverses=None,
    timestamp=None,
) -> ScoreTransaction:
    return ScoreTransaction(
        sequence=sequence,
        team_id=team_id,
        team_name=team_name,
        amount=amount,
        reason=reason,
        timestamp=timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        resulting_score=resulting_score,
        kind=kind,
        reverses=reverses,
    )


def build_undo(transaction, current_score, sequence, timestamp=None) -> ScoreTransaction:
    """Create the compensating entry for an existing transaction."""
    return new_transaction(
        sequence=sequence,
        team_id=transaction.team_id,
        team_name=transaction.team_name,
        amount=-transaction.amount,
        reason=f"Undo #{transaction.sequence}",
        resulting_score=current_score - transaction.amount,
        kind="undo",
        reverses=transaction.sequence,
        timestamp=timestamp,
    )


def mark_undone(transaction) -> ScoreTransaction:
    return replace(transaction, undone=True)
