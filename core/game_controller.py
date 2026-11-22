from PySide6.QtCore import QObject, Signal
from core.game_state import GameState

class GameController(QObject):
    state_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.state = GameState()

    def _emit(self):
        self.state_changed.emit(self.state)

    def set_question(self, question_id: str, question: str, answer: str):
        self.state.current_question_id = question_id
        self.state.question_text = question
        self.state.answer_text = answer
        self.state.question_visible = False
        self.state.answer_visible = False
        self._emit()

    def show_question(self):
        if self.state.current_question_id is None:
            return
        self.state.question_visible = True
        self._emit()

    def reveal_answer(self):
        if not self.state.question_visible:
            return
        self.state.answer_visible = True
        self._emit()

    def hide_answer(self):
        self.state.answer_visible = False
        self._emit()

    def reset(self):
        self.state = GameState()
        self._emit()
