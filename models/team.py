"""Team identity and naming rules for live quiz events.

Pure model layer: no Qt and no widget imports.
"""

from dataclasses import dataclass

# 12 cards remain readable on a 16:9 stage screen; beyond that the public
# scoreboard stops being legible from a distance. This is a display-driven
# limit, not an arbitrary business restriction.
MAX_TEAMS = 12
MAX_NAME_LENGTH = 40


@dataclass
class TeamState:
    id: int = 0
    name: str = ""
    score: int = 0


def normalize_team_name(raw) -> str:
    """Trim and collapse whitespace, then validate a team name."""
    if not isinstance(raw, str):
        raise ValueError("Nama tim harus berupa teks.")
    name = " ".join(raw.split())
    if not name:
        raise ValueError("Nama tim tidak boleh kosong.")
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Nama tim maksimal {MAX_NAME_LENGTH} karakter.")
    return name


def is_duplicate_name(teams, name, exclude_id=None) -> bool:
    """Case-insensitive duplicate check, optionally ignoring one team (rename)."""
    target = name.casefold()
    return any(
        team.id != exclude_id and team.name.casefold() == target for team in teams
    )


def validate_initial_score(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Skor awal harus berupa bilangan bulat.")
    return value
