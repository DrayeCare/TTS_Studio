"""Central, UI-independent state for a live TTS session."""

from dataclasses import dataclass, field, fields

from core.score_engine import ScoreTransaction
from models.question import Question
from models.team import TeamState  # re-exported: legacy import path stays valid


@dataclass
class GameState:
    current_question_id: str | None = None
    question_visible: bool = False
    answer_visible: bool = False
    game_started: bool = False
    game_paused: bool = False
    teams: list[TeamState] = field(default_factory=list)
    completed_questions: list[str] = field(default_factory=list)
    question_text: str = ""
    answer_text: str = ""
    title: str = ""
    questions: list[Question] = field(default_factory=list)
    current_index: int | None = None
    score_history: list[ScoreTransaction] = field(default_factory=list)
    next_team_id: int = 1
    next_transaction_id: int = 1
    selected_team_id: int | None = None
    last_action: str = ""

    def reset(self) -> None:
        """Restore defaults in place so subscribers keep a valid reference."""
        fresh = type(self)()
        for item in fields(self):
            setattr(self, item.name, getattr(fresh, item.name))
