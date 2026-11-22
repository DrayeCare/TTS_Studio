from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel

class OperatorWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("TTS Studio | Operator")
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(QLabel("Operator Console — Foundation Build"))
        show_question = QPushButton("Show Question")
        show_question.clicked.connect(controller.show_question)
        reveal = QPushButton("Reveal Answer")
        reveal.clicked.connect(controller.reveal_answer)
        hide = QPushButton("Hide Answer")
        hide.clicked.connect(controller.hide_answer)
        reset = QPushButton("Reset Game")
        reset.clicked.connect(controller.reset)
        layout.addWidget(show_question)
        layout.addWidget(reveal)
        layout.addWidget(hide)
        layout.addWidget(reset)
        self.setCentralWidget(root)
        self.resize(480, 360)
