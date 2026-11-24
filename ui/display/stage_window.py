"""Public stage display. Renders GameState without exposing operator controls."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.display.scoreboard_view import ScoreboardView


class StageWindow(QWidget):
    def __init__(self, initial_state):
        super().__init__()
        self.setWindowTitle("TTS Studio | Stage")
        self.setStyleSheet("background:#0b1220;color:#f5f7fa;")
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(64, 48, 64, 48)
        self.root_layout.setSpacing(28)

        self.title = QLabel("")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size:22px;color:#8bd49c;letter-spacing:2px;")

        self.question = QLabel("TTS STUDIO")
        self.question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question.setWordWrap(True)
        self.question.setStyleSheet("font-size:60px;font-weight:700;")

        self.answer = QLabel("")
        self.answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer.setWordWrap(True)
        self.answer.setStyleSheet("font-size:36px;color:#8bd49c;")

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("font-size:18px;color:#9aa7bd;")

        self.scoreboard = ScoreboardView()
        self.root_layout.addWidget(self.title)
        self.root_layout.addWidget(self.question, 3)
        self.root_layout.addWidget(self.answer, 1)
        self.root_layout.addWidget(self.status)
        self.root_layout.addWidget(self.scoreboard, 1)

        self.resize(1280, 720)
        self.render_state(initial_state)

    def show_on_secondary_screen(self):
        screens = QGuiApplication.screens()
        if len(screens) > 1:
            geometry = screens[1].geometry()
            self.setGeometry(geometry)
            self.showFullScreen()
        else:
            self.show()

    def render_state(self, state):
        self.title.setText(state.title.upper() if state.title else "")

        question = None
        if state.current_index is not None and 0 <= state.current_index < len(state.questions):
            question = state.questions[state.current_index]

        if state.question_visible and state.question_text:
            heading = f"SOAL {question.number}" if question else "SOAL"
            if question and question.category:
                heading += f" • {question.category.upper()}"
            self.question.setText(f"{heading}\n{state.question_text}")
        else:
            self.question.setText("TTS STUDIO")

        self.answer.setText(state.answer_text if state.answer_visible else "")

        if state.game_paused:
            self.status.setText("DIJEDA")
        elif state.game_started:
            done = len(state.completed_questions)
            self.status.setText(f"{done}/{len(state.questions)} selesai")
        else:
            self.status.setText("")

        self.scoreboard.render_state(state)
