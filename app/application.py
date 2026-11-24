"""Wires the controller, operator console, and stage display together."""

from pathlib import Path

from core.game_controller import GameController
from services.session_autosave import SessionAutosave
from services.session_service import DEFAULT_SESSION_PATH, load_session
from ui.display.stage_window import StageWindow
from ui.operator.main_window import OperatorWindow


class TTSStudioApplication:
    def __init__(self, session_path=None, backup_path=None, autosave_ms=400):
        self.session_path = Path(session_path) if session_path else DEFAULT_SESSION_PATH
        if backup_path is not None:
            self.backup_path = Path(backup_path)
        elif session_path is not None:
            self.backup_path = None  # service derives a sibling backup file
        else:
            self.backup_path = DEFAULT_SESSION_PATH.with_name(
                DEFAULT_SESSION_PATH.stem + ".backup" + DEFAULT_SESSION_PATH.suffix
            )

        self.controller = GameController()
        self.operator = OperatorWindow(self.controller)
        self.stage = StageWindow(self.controller.state)
        self.controller.state_changed.connect(self.stage.render_state)

        # Restore before autosave attaches, then apply in one emission so both
        # windows render the restored session through the normal signal path.
        self.session_result = load_session(self.session_path, self.backup_path)
        if self.session_result.state is not None:
            self.controller.apply_state(self.session_result.state)

        self.autosave = SessionAutosave(
            self.session_path, backup_path=self.backup_path, interval_ms=autosave_ms
        )
        self.autosave.mark_saved(self.controller.state)
        self.autosave.attach(self.controller)
        self.autosave.status.connect(self.operator.set_session_status)
        self.autosave.failure.connect(self.operator.set_session_error)
        self.operator.set_session_status(self.session_result.message)
        self.operator.new_session_requested.connect(self._start_fresh_session)

    def show(self):
        self.operator.show()
        self.stage.show_on_secondary_screen()

    def _start_fresh_session(self):
        """Archive the recoverable session before wiping live state."""
        self.autosave.archive()
        self.controller.reset()
