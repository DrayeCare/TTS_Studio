"""Debounced autosave running on the Qt UI thread.

No worker thread is used: controller signals are emitted synchronously on the
UI thread, the payload is small, and a single-shot QTimer coalesces bursts.
A pending timer is cancelled and written immediately on application quit.
"""

import json
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QObject, QTimer, Signal

from services.session_service import (
    SessionError,
    archive_current_session,
    save_session,
    serialize_session,
)


class SessionAutosave(QObject):
    status = Signal(str)
    failure = Signal(str)

    def __init__(self, path, backup_path=None, interval_ms=400, parent=None):
        super().__init__(parent)
        self.path = Path(path)
        self.backup_path = backup_path
        self._state = None
        self._last_payload = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.flush)

    def attach(self, controller):
        controller.state_changed.connect(self.schedule)
        app = QCoreApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.flush)

    def mark_saved(self, state):
        """Record a baseline so a restored session is not rewritten on startup."""
        self._state = state
        self._last_payload = self._payload(state)

    def schedule(self, state):
        self._state = state
        self._timer.start()

    @staticmethod
    def _payload(state):
        return json.dumps(serialize_session(state), ensure_ascii=False, sort_keys=True)

    def flush(self):
        self._timer.stop()
        if self._state is None:
            return
        payload = self._payload(self._state)
        if payload == self._last_payload:
            return
        try:
            save_session(self.path, self._state, self.backup_path)
        except SessionError as exc:
            self.failure.emit(str(exc))
            return
        self._last_payload = payload
        self.status.emit("Sesi tersimpan otomatis.")

    def archive(self):
        try:
            return archive_current_session(self.path)
        except SessionError as exc:
            self.failure.emit(str(exc))
            return None
