"""Public scoreboard widget for the stage display."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class ScoreboardView(QWidget):
    """Renders team names and scores; independent of operator widgets."""

    def __init__(self):
        super().__init__()
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(14)
        self._cards = {}
        self.setVisible(False)

    def _clear(self):
        for card, _, _ in self._cards.values():
            self._layout.removeWidget(card)
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()

    def _make_card(self, team):
        card = QFrame()
        card.setStyleSheet("QFrame { background:#152033; border-radius:12px; }")
        inner = QVBoxLayout(card)
        inner.setContentsMargins(18, 12, 18, 12)
        inner.setSpacing(2)

        name = QLabel(team.name.upper())
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setStyleSheet("font-size:15px;color:#9aa7bd;font-weight:600;")

        score = QLabel(str(team.score))
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score.setStyleSheet("font-size:34px;color:#8bd49c;font-weight:700;")

        inner.addWidget(name)
        inner.addWidget(score)
        self._layout.addWidget(card, 1)
        return card, name, score

    def render_state(self, state):
        ids = [team.id for team in state.teams]
        if set(ids) != set(self._cards):
            self._clear()
            for team in state.teams:
                self._cards[team.id] = self._make_card(team)

        for team in state.teams:
            _, name, score = self._cards[team.id]
            name.setText(team.name.upper())
            score.setText(str(team.score))

        self.setVisible(bool(state.teams))
