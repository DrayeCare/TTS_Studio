from dataclasses import dataclass, field

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
