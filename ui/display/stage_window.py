from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

class StageWindow(QWidget):
    def __init__(self, initial_state):
        super().__init__()
        self.setWindowTitle("TTS Studio | Stage")
        self.setStyleSheet("background:#10141c;color:white;")
        self.layout = QVBoxLayout(self)
        self.question = QLabel("TTS STUDIO")
        self.question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question.setStyleSheet("font-size:40px;font-weight:700;")
        self.answer = QLabel("")
        self.answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer.setStyleSheet("font-size:30px;color:#8bd49c;")
        self.layout.addWidget(self.question)
        self.layout.addWidget(self.answer)
        self.resize(900, 600)
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
        if state.question_visible:
            self.question.setText(state.question_text)
        else:
            self.question.setText("TTS STUDIO")
        self.answer.setText(state.answer_text if state.answer_visible else "")
