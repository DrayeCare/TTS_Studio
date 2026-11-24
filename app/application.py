"""Wires the controller, operator console, and stage display together."""

from core.game_controller import GameController
from ui.display.stage_window import StageWindow
from ui.operator.main_window import OperatorWindow


class TTSStudioApplication:
    def __init__(self):
        self.controller = GameController()
        self.operator = OperatorWindow(self.controller)
        self.stage = StageWindow(self.controller.state)
        self.controller.state_changed.connect(self.stage.render_state)

    def show(self):
        self.operator.show()
        self.stage.show_on_secondary_screen()
