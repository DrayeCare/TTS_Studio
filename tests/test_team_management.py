"""Team lifecycle rules, exercised through the controller."""

import pytest

from core.game_controller import GameController
from models.team import MAX_TEAMS


@pytest.fixture
def controller():
    return GameController()


def observe(controller):
    seen = []
    controller.state_changed.connect(lambda state: seen.append(state))
    return seen


def test_add_team_assigns_stable_id_and_initial_score(controller):
    seen = observe(controller)

    team_id = controller.add_team("  Tim  Alpha  ", 25)

    assert team_id == 1
    assert len(controller.state.teams) == 1
    team = controller.state.teams[0]
    assert team.id == 1
    assert team.name == "Tim Alpha"
    assert team.score == 25
    assert controller.state.selected_team_id == 1
    assert controller.selected_team is team
    assert "ditambahkan" in controller.state.last_action
    assert seen == [controller.state]


@pytest.mark.parametrize("name", ["", "   ", None, 123, "x" * 41])
def test_invalid_names_are_rejected_without_mutating(controller, name):
    seen = observe(controller)

    assert controller.add_team(name) is False
    assert controller.state.teams == []
    assert controller.state.next_team_id == 1
    assert controller.state.selected_team_id is None
    assert len(seen) == 1  # feedback is still emitted


@pytest.mark.parametrize("score", [True, "10", 1.5, None])
def test_invalid_initial_score_is_rejected(controller, score):
    assert controller.add_team("Alpha", score) is False
    assert controller.state.teams == []


def test_duplicate_names_are_case_insensitive(controller):
    controller.add_team("Tim Alpha")

    assert controller.add_team("tIM   aLPHA") is False
    assert len(controller.state.teams) == 1
    assert "sudah ada" in controller.state.last_action


def test_rename_team_keeps_id_and_allows_same_name(controller):
    controller.add_team("Alpha")

    assert controller.rename_team(1, "  Beta  ") is True
    assert controller.state.teams[0].id == 1
    assert controller.state.teams[0].name == "Beta"
    assert controller.rename_team(1, "Beta") is True


def test_rename_rejects_duplicate_and_invalid_names(controller):
    controller.add_team("Alpha")
    controller.add_team("Beta")

    assert controller.rename_team(1, "bEtA") is False
    assert controller.rename_team(1, "") is False
    assert controller.state.teams[0].name == "Alpha"


def test_rename_unknown_team_is_rejected(controller):
    assert controller.rename_team(99, "Alpha") is False
    assert controller.state.teams == []


def test_remove_team_reassigns_selection(controller):
    controller.add_team("Alpha")
    controller.add_team("Beta")
    controller.select_team(2)

    assert controller.remove_team(2) is True
    assert [team.name for team in controller.state.teams] == ["Alpha"]
    assert controller.state.selected_team_id == 1

    assert controller.remove_team(1) is True
    assert controller.state.selected_team_id is None
    assert controller.state.teams == []


def test_remove_unknown_team_is_rejected(controller):
    assert controller.remove_team(99) is False


def test_team_limit_is_enforced(controller):
    for number in range(MAX_TEAMS):
        assert controller.add_team(f"Tim {number + 1}") == number + 1

    assert controller.add_team("Tim Tambahan") is False
    assert len(controller.state.teams) == MAX_TEAMS
    assert f"maksimal {MAX_TEAMS}" in controller.state.last_action


def test_select_team_rejects_unknown_and_bool_ids(controller):
    controller.add_team("Alpha")

    assert controller.select_team(1) is True
    assert controller.select_team(99) is False
    assert controller.select_team(True) is False
    assert controller.state.selected_team_id == 1


def test_reset_clears_team_fields_in_place(controller):
    controller.add_team("Alpha", 50)
    state = controller.state

    controller.reset()

    assert controller.state is state
    assert state.teams == []
    assert state.selected_team_id is None
    assert state.next_team_id == 1
    assert state.last_action == ""
