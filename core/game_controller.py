"""Commands that mutate GameState and notify UI subscribers.

This module stays free of Qt widget imports so the gameplay rules can be
tested without a GUI.
"""

from PySide6.QtCore import QObject, Signal

from core.game_state import GameState


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
