"""Operator console: the control surface for a live TTS session."""

import html
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from services.question_service import QuestionSetError, load_question_set
from ui.components.team_panel import TeamPanel

SAMPLE_SET = Path(__file__).resolve().parents[2] / "data" / "questions" / "sample_questions.json"


class OperatorWindow(QMainWindow):
    new_session_requested = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._updating = False
        self._last_path = None
        self.setWindowTitle("TTS Studio | Operator")
        self._build_ui()
        controller.state_changed.connect(self._sync)
        self._sync(controller.state)
        self.resize(960, 640)

    def _build_ui(self):
        root = QWidget()
        outer = QVBoxLayout(root)

        self.status = QLabel("Belum ada set soal dimuat.")
        self.status.setWordWrap(True)
        outer.addWidget(self.status)

        self.session_status = QLabel("")
        self.session_status.setWordWrap(True)
        outer.addWidget(self.session_status)

        body = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Daftar Soal"))
        self.question_list = QListWidget()
        self.question_list.currentRowChanged.connect(self._on_row_changed)
        left.addWidget(self.question_list)
        body.addLayout(left, 1)

        tabs = QTabWidget()
        question_tab = QWidget()
        question_layout = QVBoxLayout(question_tab)
        question_layout.addWidget(QLabel("Detail Soal"))
        self.detail = QTextBrowser()
        self.detail.setOpenExternalLinks(False)
        question_layout.addWidget(self.detail)
        tabs.addTab(question_tab, "Soal")
        self.team_panel = TeamPanel(self.controller)
        tabs.addTab(self.team_panel, "Tim & Skor")
        body.addWidget(tabs, 2)
        outer.addLayout(body, 1)

        file_row = QHBoxLayout()
        self.load_button = QPushButton("Muat Set JSON…")
        self.load_button.clicked.connect(self._load_set)
        self.sample_button = QPushButton("Muat Contoh")
        self.sample_button.clicked.connect(self._load_sample)
        self.new_session_button = QPushButton("Sesi Baru")
        self.new_session_button.clicked.connect(self._new_session)
        file_row.addWidget(self.load_button)
        file_row.addWidget(self.sample_button)
        file_row.addWidget(self.new_session_button)
        file_row.addStretch(1)
        outer.addLayout(file_row)

        control_row = QHBoxLayout()
        self.start_button = QPushButton("Mulai")
        self.start_button.clicked.connect(self.controller.start_game)
        self.pause_button = QPushButton("Jeda")
        self.pause_button.clicked.connect(self.controller.pause_game)
        self.resume_button = QPushButton("Lanjut")
        self.resume_button.clicked.connect(self.controller.resume_game)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._reset)
        for button in (self.start_button, self.pause_button, self.resume_button, self.reset_button):
            control_row.addWidget(button)
        outer.addLayout(control_row)

        question_row = QHBoxLayout()
        self.previous_button = QPushButton("Sebelumnya")
        self.previous_button.clicked.connect(self.controller.previous_question)
        self.next_button = QPushButton("Berikutnya")
        self.next_button.clicked.connect(self.controller.next_question)
        self.show_button = QPushButton("Tampilkan Soal")
        self.show_button.clicked.connect(self.controller.show_question)
        self.reveal_button = QPushButton("Buka Jawaban")
        self.reveal_button.clicked.connect(self.controller.reveal_answer)
        self.hide_button = QPushButton("Sembunyikan Jawaban")
        self.hide_button.clicked.connect(self.controller.hide_answer)
        self.complete_button = QPushButton("Tandai Selesai")
        self.complete_button.clicked.connect(self.controller.mark_completed)
        for button in (
            self.previous_button, self.next_button, self.show_button,
            self.reveal_button, self.hide_button, self.complete_button,
        ):
            question_row.addWidget(button)
        outer.addLayout(question_row)

        self.setCentralWidget(root)
        self._install_shortcuts()

    def _install_shortcuts(self):
        bindings = {
            "Left": self._shortcut_previous,
            "Right": self._shortcut_next,
            "S": self.controller.show_question,
            "R": self.controller.reveal_answer,
            "H": self.controller.hide_answer,
        }
        for sequence, handler in bindings.items():
            QShortcut(QKeySequence(sequence), self, handler)

    # Arrow shortcuts must not fight the list widget's own navigation.
    def _shortcut_previous(self):
        if not self.question_list.hasFocus():
            self.controller.previous_question()

    def _shortcut_next(self):
        if not self.question_list.hasFocus():
            self.controller.next_question()

    # --- user actions --------------------------------------------------

    def _on_row_changed(self, row):
        if not self._updating and row >= 0:
            self.controller.select_question(row)

    def _load_set(self):
        start_dir = str(self._last_path.parent) if self._last_path else ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih set soal", start_dir, "File JSON (*.json)"
        )
        if path:
            self._load_path(path)

    def _load_sample(self):
        self._load_path(SAMPLE_SET)

    def _load_path(self, path):
        try:
            question_set = load_question_set(path)
        except QuestionSetError as exc:
            QMessageBox.warning(self, "Set soal gagal dimuat", str(exc))
            return
        self._last_path = Path(path)
        self.controller.load_question_set(question_set.title, question_set.questions)

    def _reset(self):
        answer = QMessageBox.question(
            self,
            "Reset permainan",
            "Kembalikan seluruh state ke awal? Set soal yang dimuat akan dibatalkan.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.controller.reset()

    # --- persistence feedback ----------------------------------------

    def set_session_status(self, text):
        self.session_status.setText(text)

    def set_session_error(self, text):
        self.session_status.setText(f"Gagal menyimpan: {text}")

    def _new_session(self):
        answer = QMessageBox.question(
            self,
            "Sesi baru",
            "Mulai sesi baru? Sesi sebelumnya akan diarsipkan sebagai cadangan.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.new_session_requested.emit()

    # --- state rendering ----------------------------------------------

    @staticmethod
    def _item_text(index, question, state):
        if question.id in state.completed_questions:
            mark = "✓"
        elif index == state.current_index:
            mark = "●"
        else:
            mark = "○"
        return f"{mark} {question.number}. [{question.category}] {question.question}"

    def _sync(self, state):
        self._updating = True
        try:
            self._sync_list(state)
            self._sync_detail(state)
            self._sync_status(state)
            self._sync_buttons(state)
            self.team_panel.sync(state)
        finally:
            self._updating = False

    def _sync_list(self, state):
        ids = [question.id for question in state.questions]
        shown = [
            self.question_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.question_list.count())
        ]
        if shown != ids:
            self.question_list.clear()
            for index, question in enumerate(state.questions):
                item = QListWidgetItem(self._item_text(index, question, state))
                item.setData(Qt.ItemDataRole.UserRole, question.id)
                self.question_list.addItem(item)
        else:
            for index, question in enumerate(state.questions):
                self.question_list.item(index).setText(
                    self._item_text(index, question, state)
                )

        if state.current_index is None:
            self.question_list.clearSelection()
        elif 0 <= state.current_index < self.question_list.count():
            self.question_list.setCurrentRow(state.current_index)

    def _sync_detail(self, state):
        question = self.controller.current_question
        if question is None:
            self.detail.setHtml("<p>Pilih soal untuk melihat detail.</p>")
            return
        parts = [
            f"<h3>Soal {question.number} — {html.escape(question.category)}</h3>",
            f"<p>{html.escape(question.question)}</p>",
        ]
        if question.hint:
            parts.append(f"<p><b>Petunjuk:</b> {html.escape(question.hint)}</p>")
        if question.notes:
            parts.append(f"<p><i>Catatan operator:</i> {html.escape(question.notes)}</p>")
        answer = html.escape(question.answer) if state.answer_visible else "••••••"
        parts.append(f"<p><b>Jawaban:</b> {answer}</p>")
        self.detail.setHtml("".join(parts))

    def _sync_status(self, state):
        total = len(state.questions)
        done = len(state.completed_questions)
        pieces = []
        if state.title:
            pieces.append(state.title)
        pieces.append(f"{done}/{total} selesai")
        if not state.game_started:
            pieces.append("belum dimulai")
        elif state.game_paused:
            pieces.append("DIJEDA")
        else:
            pieces.append("BERJALAN")
        if state.question_visible:
            pieces.append("soal tampil" if not state.answer_visible else "jawaban tampil")
        self.status.setText(" • ".join(pieces))

    def _sync_buttons(self, state):
        total = len(state.questions)
        index = state.current_index
        question = self.controller.current_question
        self.previous_button.setEnabled(index is not None and index > 0)
        self.next_button.setEnabled(index is not None and index + 1 < total)
        self.show_button.setEnabled(question is not None and not state.question_visible)
        self.reveal_button.setEnabled(state.question_visible and not state.answer_visible)
        self.hide_button.setEnabled(state.answer_visible)
        self.complete_button.setEnabled(
            question is not None and question.id not in state.completed_questions
        )
        self.start_button.setEnabled(not state.game_started and total > 0)
        self.pause_button.setEnabled(state.game_started and not state.game_paused)
        self.resume_button.setEnabled(state.game_paused)
