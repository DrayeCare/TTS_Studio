"""Commands that mutate GameState and notify UI subscribers.

This module stays free of Qt widget imports so the gameplay rules can be
tested without a GUI.
"""

from dataclasses import fields

from PySide6.QtCore import QObject, Signal

from core.game_state import GameState
from core.score_engine import (
    build_undo,
    mark_undone,
    new_transaction,
    validate_amount,
    validate_reason,
)
from models.team import (
    MAX_TEAMS,
    TeamState,
    is_duplicate_name,
    normalize_team_name,
    validate_initial_score,
)


class GameController(QObject):
    state_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.state = GameState()

    def _emit(self):
        self.state_changed.emit(self.state)

    # --- question set -------------------------------------------------

    def load_question_set(self, title, questions):
        """Replace the current set and clear all progress."""
        state = self.state
        state.title = title
        state.questions = list(questions)
        state.current_index = None
        state.current_question_id = None
        state.question_text = ""
        state.answer_text = ""
        state.question_visible = False
        state.answer_visible = False
        state.completed_questions = []
        state.game_started = False
        state.game_paused = False
        self._emit()

    @property
    def current_question(self):
        index = self.state.current_index
        if index is None or not 0 <= index < len(self.state.questions):
            return None
        return self.state.questions[index]

    def select_question(self, index):
        """Select a question by its position in the set."""
        if isinstance(index, bool) or not isinstance(index, int):
            return False
        if not 0 <= index < len(self.state.questions):
            return False
        question = self.state.questions[index]
        state = self.state
        state.current_index = index
        state.current_question_id = question.id
        state.question_text = question.question
        state.answer_text = question.answer
        state.question_visible = False
        state.answer_visible = False
        self._emit()
        return True

    def set_question(self, question_id: str, question: str, answer: str):
        """Manual single-question entry (original controller API, preserved)."""
        state = self.state
        state.current_question_id = question_id
        state.question_text = question
        state.answer_text = answer
        state.current_index = next(
            (i for i, item in enumerate(state.questions) if item.id == question_id), None
        )
        state.question_visible = False
        state.answer_visible = False
        self._emit()

    def next_question(self):
        index = self.state.current_index
        return self.select_question(0 if index is None else index + 1)

    def previous_question(self):
        index = self.state.current_index
        if index is None or index <= 0:
            return False
        return self.select_question(index - 1)

    def mark_completed(self):
        question = self.current_question
        if question is None or question.id in self.state.completed_questions:
            return False
        self.state.completed_questions.append(question.id)
        self._emit()
        return True

    # --- display and session flow -------------------------------------

    def show_question(self):
        if self.current_question is None:
            return False
        self.state.question_visible = True
        self._emit()
        return True

    def reveal_answer(self):
        if not self.state.question_visible:
            return False
        self.state.answer_visible = True
        self._emit()
        return True

    def hide_answer(self):
        if not self.state.answer_visible:
            return False
        self.state.answer_visible = False
        self._emit()
        return True

    def start_game(self):
        if not self.state.questions:
            return False
        self.state.game_started = True
        self.state.game_paused = False
        self._emit()
        return True

    def pause_game(self):
        if not self.state.game_started or self.state.game_paused:
            return False
        self.state.game_paused = True
        self._emit()
        return True

    def resume_game(self):
        if not self.state.game_started or not self.state.game_paused:
            return False
        self.state.game_paused = False
        self._emit()
        return True

    def reset(self):
        """Return the whole session to its initial state."""
        self.state.reset()
        self._emit()

    def apply_state(self, state):
        """Adopt a fully validated state in place and notify subscribers once."""
        for item in fields(self.state):
            setattr(self.state, item.name, getattr(state, item.name))
        self._emit()

    # --- team management ---------------------------------------------

    def _fail(self, message):
        """Reject a command but still report why through state feedback."""
        self.state.last_action = message
        self._emit()
        return False

    def _find_team(self, team_id):
        if isinstance(team_id, bool) or not isinstance(team_id, int):
            return None
        return next((team for team in self.state.teams if team.id == team_id), None)

    def add_team(self, name, score=0):
        """Create a team. Returns its id, or False when rejected."""
        try:
            clean_name = normalize_team_name(name)
            score = validate_initial_score(score)
        except ValueError as exc:
            return self._fail(str(exc))
        if len(self.state.teams) >= MAX_TEAMS:
            return self._fail(f"Jumlah tim maksimal {MAX_TEAMS}.")
        if is_duplicate_name(self.state.teams, clean_name):
            return self._fail(f"Tim '{clean_name}' sudah ada.")
        team = TeamState(id=self.state.next_team_id, name=clean_name, score=score)
        self.state.next_team_id += 1
        self.state.teams.append(team)
        if self.state.selected_team_id is None:
            self.state.selected_team_id = team.id
        self.state.last_action = f"Tim '{team.name}' ditambahkan."
        self._emit()
        return team.id

    def rename_team(self, team_id, name):
        team = self._find_team(team_id)
        if team is None:
            return self._fail("Tim tidak ditemukan.")
        try:
            clean_name = normalize_team_name(name)
        except ValueError as exc:
            return self._fail(str(exc))
        if is_duplicate_name(self.state.teams, clean_name, exclude_id=team_id):
            return self._fail(f"Tim '{clean_name}' sudah ada.")
        old_name = team.name
        team.name = clean_name
        self.state.last_action = f"Tim '{old_name}' menjadi '{clean_name}'."
        self._emit()
        return True

    def remove_team(self, team_id):
        team = self._find_team(team_id)
        if team is None:
            return self._fail("Tim tidak ditemukan.")
        self.state.teams.remove(team)
        if self.state.selected_team_id == team_id:
            self.state.selected_team_id = (
                self.state.teams[0].id if self.state.teams else None
            )
        self.state.last_action = f"Tim '{team.name}' dihapus."
        self._emit()
        return True

    def select_team(self, team_id):
        team = self._find_team(team_id)
        if team is None:
            return self._fail("Tim tidak ditemukan.")
        self.state.selected_team_id = team.id
        self.state.last_action = f"Tim '{team.name}' dipilih."
        self._emit()
        return True

    @property
    def selected_team(self):
        return self._find_team(self.state.selected_team_id)

    # --- scoring ------------------------------------------------------

    def adjust_score(self, team_id, amount, reason=""):
        """Apply one validated score transaction to a team."""
        team = self._find_team(team_id)
        if team is None:
            return self._fail("Tim tidak ditemukan.")
        try:
            amount = validate_amount(amount)
            reason = validate_reason(reason)
        except ValueError as exc:
            return self._fail(str(exc))
        resulting_score = team.score + amount
        transaction = new_transaction(
            sequence=self.state.next_transaction_id,
            team_id=team.id,
            team_name=team.name,
            amount=amount,
            reason=reason,
            resulting_score=resulting_score,
        )
        team.score = resulting_score
        self.state.next_transaction_id += 1
        self.state.score_history.append(transaction)
        self.state.last_action = f"{team.name}: {amount:+d} poin ({reason})."
        self._emit()
        return True

    def undo_last_score(self):
        """Reverse the newest active score transaction with a ledger entry."""
        state = self.state
        target_index = -1
        target = None
        for index, transaction in enumerate(state.score_history):
            if transaction.kind == "score" and not transaction.undone:
                target_index = index
                target = transaction
        if target is None:
            return self._fail("Tidak ada transaksi skor yang bisa di-undo.")
        team = self._find_team(target.team_id)
        if team is None:
            return self._fail("Tim dari transaksi tersebut sudah dihapus.")
        undo_entry = build_undo(target, team.score, state.next_transaction_id)
        state.score_history[target_index] = mark_undone(target)
        team.score = undo_entry.resulting_score
        state.next_transaction_id += 1
        state.score_history.append(undo_entry)
        state.last_action = f"Undo transaksi #{target.sequence} ({target.team_name})."
        self._emit()
        return True
