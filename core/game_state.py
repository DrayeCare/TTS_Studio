"""Central, UI-independent state for a live TTS session."""

from dataclasses import dataclass, field, fields

from models.question import Question


@dataclass
class TeamState:
    name: str
    score: int = 0


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

    def reset(self) -> None:
        """Restore defaults in place so subscribers keep a valid reference."""
        fresh = type(self)()
        for item in fields(self):
            setattr(self, item.name, getattr(fresh, item.name))
