"""Versioned JSON persistence and recovery for TTS Studio sessions.

The service owns all session file I/O. It never imports Qt widgets and never
mutates controller state: deserialization builds a fresh, fully validated
GameState that the caller may apply atomically.

Schema contract (version 1)
---------------------------
The payload is a JSON object with ``schema_version: 1`` and these fields:
title, questions, current_question_id, current_index, question_text,
answer_text, question_visible, answer_visible, game_started, game_paused,
completed_questions, teams, selected_team_id, next_team_id, score_history,
next_transaction_id.

``question_text`` and ``answer_text`` are stored even though they normally
mirror the selected question: the public ``set_question()`` API can set text
that is not present in the question set, so reconstructing them would lose
data. ``last_action`` is transient operator feedback and is intentionally not
stored. Undo is represented entirely by the append-only ledger (the original
entry is flagged ``undone`` and a compensating ``undo`` entry is appended),
so no separate undo stack is needed.

Safe-write policy
-----------------
A new payload is written to a unique temp file in the target directory,
flushed and fsynced before it replaces the target. When the primary file is
still valid it is copied to the backup *before* the primary is replaced, so a
failed write cannot destroy the last known good session. ``os.replace`` is
atomic on the same filesystem where the platform supports it; no claim is
made that every Windows filesystem guarantees atomic replacement.
"""

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from core.game_state import GameState
from core.score_engine import (
    MAX_REASON_LENGTH,
    ScoreTransaction,
    validate_amount,
    validate_reason,
)
from models.question import Question
from models.team import MAX_TEAMS, TeamState, normalize_team_name

SESSION_VERSION = 1
SESSION_FILENAME = "session.json"
BACKUP_FILENAME = "session.backup.json"

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SESSION_PATH = ROOT / "data" / "session" / SESSION_FILENAME
DEFAULT_BACKUP_PATH = ROOT / "data" / "session" / BACKUP_FILENAME


class SessionError(ValueError):
    """Raised for any unreadable, invalid, or unwritable session data."""


@dataclass
class SessionLoadResult:
    state: GameState | None
    source: str  # "primary", "backup" or "none"
    message: str
    damaged: list[Path] = field(default_factory=list)


def _require(condition, message):
    if not condition:
        raise SessionError(message)


def _as_int(value, name, minimum=None, allow_none=False):
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise SessionError(f"{name} harus berupa bilangan bulat.")
    if minimum is not None and value < minimum:
        raise SessionError(f"{name} harus >= {minimum}.")
    return value


def _as_bool(value, name):
    if not isinstance(value, bool):
        raise SessionError(f"{name} harus berupa boolean.")
    return value


def _as_text(value, name):
    if not isinstance(value, str):
        raise SessionError(f"{name} harus berupa teks.")
    return value


def _backup_for(primary, backup_path):
    return Path(backup_path) if backup_path else primary.with_name(
        primary.stem + ".backup" + primary.suffix
    )


def _temp_for(target):
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(
            dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp"
        )
        return descriptor, Path(name)
    except OSError as exc:
        raise SessionError(f"Gagal menyiapkan penulisan {target.name}: {exc}") from exc


def _write_and_sync(target, data):
    descriptor, temp_path = _temp_for(target)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise SessionError(f"Gagal menulis {target.name}: {exc}") from exc
    return temp_path


def _replace(temp_path, target):
    try:
        os.replace(temp_path, target)
    except OSError as exc:
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise SessionError(f"Gagal mengganti {target.name}: {exc}") from exc


def _payload_bytes(state):
    payload = serialize_session(state)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")


def serialize_session(state):
    """Convert a GameState into a plain, versioned JSON-ready dictionary."""
    return {
        "schema_version": SESSION_VERSION,
        "title": state.title,
        "questions": [asdict(question) for question in state.questions],
        "current_question_id": state.current_question_id,
        "current_index": state.current_index,
        "question_text": state.question_text,
        "answer_text": state.answer_text,
        "question_visible": state.question_visible,
        "answer_visible": state.answer_visible,
        "game_started": state.game_started,
        "game_paused": state.game_paused,
        "completed_questions": list(state.completed_questions),
        "teams": [asdict(team) for team in state.teams],
        "selected_team_id": state.selected_team_id,
        "next_team_id": state.next_team_id,
        "score_history": [asdict(transaction) for transaction in state.score_history],
        "next_transaction_id": state.next_transaction_id,
    }


def _read_questions(raw_questions):
    _require(isinstance(raw_questions, list), "Field 'questions' harus berupa daftar.")
    questions = []
    seen = set()
    for position, raw in enumerate(raw_questions, start=1):
        try:
            question = Question.from_dict(raw, position)
        except ValueError as exc:
            raise SessionError(str(exc)) from exc
        _require(question.id not in seen, f"ID soal duplikat: '{question.id}'.")
        seen.add(question.id)
        questions.append(question)
    return questions, seen


def _read_teams(raw_teams):
    _require(isinstance(raw_teams, list), "Field 'teams' harus berupa daftar.")
    _require(len(raw_teams) <= MAX_TEAMS, f"Jumlah tim dalam sesi melebihi {MAX_TEAMS}.")
    teams = []
    seen_ids = set()
    seen_names = set()
    for raw in raw_teams:
        _require(isinstance(raw, dict), "Setiap tim harus berupa objek JSON.")
        team_id = _as_int(raw.get("id"), "id tim", minimum=1)
        _require(team_id not in seen_ids, f"ID tim duplikat: {team_id}.")
        try:
            name = normalize_team_name(raw.get("name"))
        except ValueError as exc:
            raise SessionError(str(exc)) from exc
        _require(name.casefold() not in seen_names, f"Nama tim duplikat: '{name}'.")
        score = _as_int(raw.get("score"), "skor tim")
        seen_ids.add(team_id)
        seen_names.add(name.casefold())
        teams.append(TeamState(id=team_id, name=name, score=score))
    return teams, seen_ids


def _validated_amount(value):
    try:
        return validate_amount(value)
    except ValueError as exc:
        raise SessionError(str(exc)) from exc


def _validated_reason(value):
    if value is None:
        value = ""
    _as_text(value, "reason transaksi")
    _require(len(value.strip()) <= MAX_REASON_LENGTH, "Alasan transaksi terlalu panjang.")
    try:
        return validate_reason(value)
    except ValueError as exc:
        raise SessionError(str(exc)) from exc


def _read_history(raw_history, team_scores, next_team_id):
    _require(isinstance(raw_history, list), "Field 'score_history' harus berupa daftar.")
    transactions = []
    sequences = set()
    previous_sequence = 0
    for raw in raw_history:
        _require(isinstance(raw, dict), "Setiap transaksi harus berupa objek JSON.")
        sequence = _as_int(raw.get("sequence"), "sequence transaksi", minimum=1)
        _require(sequence not in sequences, f"Nomor transaksi duplikat: {sequence}.")
        _require(sequence > previous_sequence, "Nomor transaksi harus meningkat.")
        team_id = _as_int(raw.get("team_id"), "team_id transaksi", minimum=1)
        # Removed teams legitimately stay referenced by their old transactions.
        _require(
            team_id < next_team_id,
            f"Transaksi #{sequence} merujuk ke tim yang tidak pernah dibuat.",
        )
        team_name = _as_text(raw.get("team_name"), "team_name transaksi")
        amount = _validated_amount(raw.get("amount"))
        reason = _validated_reason(raw.get("reason"))
        timestamp = _as_text(raw.get("timestamp"), "timestamp transaksi")
        try:
            parsed = datetime.fromisoformat(timestamp)
        except ValueError as exc:
            raise SessionError(f"Timestamp transaksi #{sequence} tidak valid.") from exc
        _require(parsed.tzinfo is not None, f"Timestamp transaksi #{sequence} harus memiliki zona waktu.")
        resulting_score = _as_int(raw.get("resulting_score"), "resulting_score transaksi")
        kind = _as_text(raw.get("kind"), "kind transaksi")
        _require(kind in ("score", "undo"), f"Jenis transaksi #{sequence} tidak dikenal.")
        reverses = _as_int(raw.get("reverses"), "reverses", allow_none=True)
        undone = _as_bool(raw.get("undone", False), "undone")
        if kind == "score":
            _require(reverses is None, f"Transaksi skor #{sequence} tidak boleh memiliki 'reverses'.")
        else:
            _require(reverses is not None, f"Transaksi undo #{sequence} harus memiliki 'reverses'.")
        transactions.append(
            ScoreTransaction(
                sequence=sequence,
                team_id=team_id,
                team_name=team_name,
                amount=amount,
                reason=reason,
                timestamp=timestamp,
                resulting_score=resulting_score,
                kind=kind,
                reverses=reverses,
                undone=undone,
            )
        )
        sequences.add(sequence)
        previous_sequence = sequence

    by_sequence = {transaction.sequence: transaction for transaction in transactions}
    undone_by_sequence = set()
    for transaction in transactions:
        if transaction.kind != "undo":
            continue
        original = by_sequence.get(transaction.reverses)
        _require(
            original is not None and original.kind == "score",
            f"Undo #{transaction.sequence} merujuk ke transaksi yang tidak ada.",
        )
        _require(original.undone, f"Transaksi #{original.sequence} belum ditandai batal.")
        _require(
            transaction.team_id == original.team_id
            and transaction.amount == -original.amount,
            f"Undo #{transaction.sequence} tidak cocok dengan transaksi aslinya.",
        )
        _require(
            original.sequence not in undone_by_sequence,
            f"Transaksi #{original.sequence} dibatalkan lebih dari sekali.",
        )
        undone_by_sequence.add(original.sequence)
    for transaction in transactions:
        if transaction.undone and transaction.kind == "score":
            _require(
                transaction.sequence in undone_by_sequence,
                f"Transaksi #{transaction.sequence} ditandai batal tanpa entri undo.",
            )

    # Ledger arithmetic: every entry changed the score when it was recorded,
    # including compensating undo entries. `undone` is metadata, so it must
    # NOT be excluded from the replay (that would double-subtract).
    for team_id in {transaction.team_id for transaction in transactions}:
        entries = [t for t in transactions if t.team_id == team_id]
        for previous, current in zip(entries, entries[1:]):
            _require(
                current.resulting_score == previous.resulting_score + current.amount,
                f"Skor transaksi #{current.sequence} tidak konsisten dengan riwayat.",
            )
        if team_id in team_scores:
            _require(
                team_scores[team_id] == entries[-1].resulting_score,
                f"Skor tim {team_id} tidak cocok dengan riwayat transaksinya.",
            )
    return transactions, sequences


def deserialize_session(data):
    """Build a completely validated GameState; raise SessionError on any fault."""
    _require(isinstance(data, dict), "Isi sesi harus berupa objek JSON.")
    version = data.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise SessionError("Versi skema sesi tidak valid.")
    if version != SESSION_VERSION:
        raise SessionError(
            f"Versi sesi {version} tidak didukung (dibutuhkan versi {SESSION_VERSION})."
        )

    title = _as_text(data.get("title", ""), "title").strip()
    questions, question_ids = _read_questions(data.get("questions", []))

    current_index = _as_int(
        data.get("current_index"), "current_index", minimum=0, allow_none=True
    )
    current_id = data.get("current_question_id")
    if current_id in ("", None):
        current_id = None
    else:
        current_id = _as_text(current_id, "current_question_id")
    if current_index is None:
        _require(current_id is None, "current_question_id tanpa current_index tidak valid.")
    else:
        _require(current_index < len(questions), "current_index di luar jangkauan soal.")
        _require(
            current_id == questions[current_index].id,
            "current_question_id tidak cocok dengan current_index.",
        )

    for field_name in ("question_visible", "answer_visible", "game_started", "game_paused"):
        _as_bool(data.get(field_name, False), field_name)

    completed = data.get("completed_questions", [])
    _require(isinstance(completed, list), "completed_questions harus berupa daftar.")
    seen_completed = set()
    for question_id in completed:
        question_id = _as_text(question_id, "completed_questions item")
        _require(question_id in question_ids, f"Soal selesai tidak dikenal: '{question_id}'.")
        _require(question_id not in seen_completed, f"Soal selesai duplikat: '{question_id}'.")
        seen_completed.add(question_id)

    teams, team_id_set = _read_teams(data.get("teams", []))
    team_scores = {team.id: team.score for team in teams}
    next_team_id = _as_int(data.get("next_team_id", 1), "next_team_id", minimum=1)
    _require(
        next_team_id > max(team_id_set) if team_id_set else next_team_id >= 1,
        "next_team_id tidak valid terhadap daftar tim.",
    )
    selected = _as_int(data.get("selected_team_id"), "selected_team_id", allow_none=True)
    _require(
        selected is None or selected in team_id_set,
        "selected_team_id tidak merujuk ke tim yang ada.",
    )

    history, sequences = _read_history(
        data.get("score_history", []), team_scores, next_team_id
    )
    next_transaction_id = _as_int(
        data.get("next_transaction_id", 1), "next_transaction_id", minimum=1
    )
    expected_next = max(sequences) + 1 if sequences else 1
    _require(
        next_transaction_id == expected_next,
        "next_transaction_id tidak konsisten dengan riwayat transaksi.",
    )

    return GameState(
        current_question_id=current_id,
        question_visible=data.get("question_visible", False),
        answer_visible=data.get("answer_visible", False),
        game_started=data.get("game_started", False),
        game_paused=data.get("game_paused", False),
        teams=teams,
        completed_questions=list(completed),
        question_text=_as_text(data.get("question_text", ""), "question_text"),
        answer_text=_as_text(data.get("answer_text", ""), "answer_text"),
        title=title,
        questions=questions,
        current_index=current_index,
        score_history=history,
        next_team_id=next_team_id,
        next_transaction_id=next_transaction_id,
        selected_team_id=selected,
    )


def save_session(path, state, backup_path=None):
    """Persist ``state`` safely, keeping the previous valid file as backup."""
    primary = Path(path)
    backup = _backup_for(primary, backup_path)
    data = _payload_bytes(state)
    try:
        deserialize_session(json.loads(data.decode("utf-8")))
    except (ValueError, UnicodeDecodeError) as exc:
        raise SessionError(f"Sesi tidak valid untuk disimpan: {exc}") from exc

    previous = None
    if primary.exists():
        try:
            candidate = primary.read_bytes()
            deserialize_session(json.loads(candidate.decode("utf-8")))
            previous = candidate
        except (OSError, ValueError, UnicodeDecodeError):
            previous = None

    new_temp = _write_and_sync(primary, data)
    backup_temp = None
    try:
        if previous is not None:
            backup_temp = _write_and_sync(backup, previous)
            _replace(backup_temp, backup)
            backup_temp = None
        _replace(new_temp, primary)
        new_temp = None
    finally:
        for temp in (new_temp, backup_temp):
            if temp is not None:
                try:
                    temp.unlink()
                except OSError:
                    pass


def _preserve_damaged(path):
    """Rename a damaged file aside so diagnostics remain possible."""
    target = path.with_name(
        f"{path.stem}.damaged-{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
    )
    try:
        os.replace(path, target)
        return target
    except OSError:
        return None


def _read_valid(path):
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SessionError(f"Gagal membaca sesi: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SessionError(
            f"JSON sesi rusak (baris {exc.lineno}, kolom {exc.colno})."
        ) from exc
    return deserialize_session(data)


def load_session(path, backup_path=None):
    """Validate the primary session, then fall back to a valid backup."""
    primary = Path(path)
    backup = _backup_for(primary, backup_path)
    damaged = []
    state = None
    source = "none"
    message = "Tidak ada sesi tersimpan. Sesi baru dimulai."
    primary_error = None

    if primary.exists():
        try:
            state = _read_valid(primary)
            source = "primary"
            message = "Sesi sebelumnya dipulihkan."
        except SessionError as exc:
            primary_error = str(exc)
            preserved = _preserve_damaged(primary)
            if preserved is not None:
                damaged.append(preserved)

    if state is None and backup.exists():
        try:
            state = _read_valid(backup)
            source = "backup"
            message = f"Sesi dipulihkan dari cadangan ({primary_error})."
        except SessionError as exc:
            preserved = _preserve_damaged(backup)
            if preserved is not None:
                damaged.append(preserved)
            message = f"Sesi utama dan cadangan rusak. Sesi baru dimulai. ({exc})"

    if state is None and primary_error is not None and not backup.exists():
        message = f"Sesi tidak dapat dipulihkan: {primary_error}. Sesi baru dimulai."

    return SessionLoadResult(state=state, source=source, message=message, damaged=damaged)


def archive_current_session(path):
    """Copy the current valid session aside before starting a fresh one."""
    primary = Path(path)
    if not primary.exists():
        return None
    try:
        candidate = primary.read_bytes()
        deserialize_session(json.loads(candidate.decode("utf-8")))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    target = primary.with_name(
        f"{primary.stem}.previous-{datetime.now().strftime('%Y%m%d_%H%M%S')}{primary.suffix}"
    )
    temp = _write_and_sync(target, candidate)
    _replace(temp, target)
    return target
