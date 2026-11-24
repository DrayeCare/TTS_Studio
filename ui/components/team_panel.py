"""Operator panel for team management and scoring."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from models.team import MAX_NAME_LENGTH


class TeamPanel(QWidget):
    """Reusable control panel; all mutations go through the controller."""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._updating = False
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        root.addWidget(QLabel("Tim"))
        self.team_list = QListWidget()
        self.team_list.currentRowChanged.connect(self._on_row_changed)
        root.addWidget(self.team_list, 2)

        add_row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama tim baru")
        self.name_input.setMaxLength(MAX_NAME_LENGTH)
        self.add_button = QPushButton("Tambah Tim")
        self.add_button.clicked.connect(self._add_team)
        add_row.addWidget(self.name_input)
        add_row.addWidget(self.add_button)
        root.addLayout(add_row)

        manage_row = QHBoxLayout()
        self.rename_button = QPushButton("Ubah Nama")
        self.rename_button.clicked.connect(self._rename_team)
        self.remove_button = QPushButton("Hapus Tim")
        self.remove_button.clicked.connect(self._remove_team)
        manage_row.addWidget(self.rename_button)
        manage_row.addWidget(self.remove_button)
        root.addLayout(manage_row)

        root.addWidget(QLabel("Penyesuaian Skor"))
        score_row = QHBoxLayout()
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(1, 9999)
        self.amount_spin.setValue(10)
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Alasan (opsional)")
        score_row.addWidget(self.amount_spin)
        score_row.addWidget(self.reason_input, 1)
        root.addLayout(score_row)

        action_row = QHBoxLayout()
        self.add_score_button = QPushButton("+ Poin")
        self.add_score_button.clicked.connect(self._add_score)
        self.subtract_score_button = QPushButton("- Poin")
        self.subtract_score_button.clicked.connect(self._subtract_score)
        self.undo_button = QPushButton("Undo Skor")
        self.undo_button.clicked.connect(self.controller.undo_last_score)
        action_row.addWidget(self.add_score_button)
        action_row.addWidget(self.subtract_score_button)
        action_row.addWidget(self.undo_button)
        root.addLayout(action_row)

        root.addWidget(QLabel("Riwayat Skor"))
        self.history = QListWidget()
        root.addWidget(self.history, 2)
        self.feedback = QLabel("")
        self.feedback.setWordWrap(True)
        root.addWidget(self.feedback)

    # --- user actions --------------------------------------------------

    def _on_row_changed(self, row):
        if self._updating or row < 0:
            return
        item = self.team_list.item(row)
        if item is not None:
            self.controller.select_team(item.data(Qt.ItemDataRole.UserRole))

    def _add_team(self):
        if self.controller.add_team(self.name_input.text()):
            self.name_input.clear()

    def _rename_team(self):
        team = self.controller.selected_team
        if team is None:
            return
        name, accepted = QInputDialog.getText(
            self, "Ubah Nama Tim", "Nama baru:", text=team.name
        )
        if accepted:
            self.controller.rename_team(team.id, name)

    def _remove_team(self):
        team = self.controller.selected_team
        if team is None:
            return
        answer = QMessageBox.question(
            self,
            "Hapus tim",
            f"Hapus tim '{team.name}'? Riwayat skor tetap disimpan.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.controller.remove_team(team.id)

    def _add_score(self):
        self.controller.adjust_score(
            self.controller.state.selected_team_id,
            self.amount_spin.value(),
            self.reason_input.text(),
        )

    def _subtract_score(self):
        self.controller.adjust_score(
            self.controller.state.selected_team_id,
            -self.amount_spin.value(),
            self.reason_input.text(),
        )

    # --- state rendering ----------------------------------------------

    def sync(self, state):
        self._updating = True
        try:
            self._sync_teams(state)
            self._sync_history(state)
            has_team = state.selected_team_id is not None
            self.rename_button.setEnabled(has_team)
            self.remove_button.setEnabled(has_team)
            self.add_score_button.setEnabled(has_team)
            self.subtract_score_button.setEnabled(has_team)
            self.undo_button.setEnabled(
                any(
                    tx.kind == "score" and not tx.undone
                    for tx in state.score_history
                )
            )
            self.feedback.setText(state.last_action)
        finally:
            self._updating = False

    def _sync_teams(self, state):
        ids = [team.id for team in state.teams]
        shown = [
            self.team_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.team_list.count())
        ]
        if shown != ids:
            self.team_list.clear()
            for team in state.teams:
                item = QListWidgetItem(f"{team.name} — {team.score}")
                item.setData(Qt.ItemDataRole.UserRole, team.id)
                self.team_list.addItem(item)
        else:
            for index, team in enumerate(state.teams):
                self.team_list.item(index).setText(f"{team.name} — {team.score}")

        if state.selected_team_id is None:
            self.team_list.clearSelection()
        elif state.selected_team_id in ids:
            self.team_list.setCurrentRow(ids.index(state.selected_team_id))

    def _sync_history(self, state):
        self.history.clear()
        for transaction in reversed(state.score_history[-50:]):
            label = (
                f"#{transaction.sequence} {transaction.team_name} "
                f"{transaction.amount:+d} → {transaction.resulting_score} "
                f"• {transaction.reason}"
            )
            if transaction.kind == "undo":
                label += " [undo]"
            elif transaction.undone:
                label += " [batal]"
            self.history.addItem(label)
