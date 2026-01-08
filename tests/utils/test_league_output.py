import json
from pathlib import Path

from player_universe_trx.models.mtbl import (
    MtblLeagueModel,
    MtblScheduleModel,
    MtblTeamRosterModel,
)
from player_universe_trx.utils import league_output


def _make_team_roster(team_id: int) -> MtblTeamRosterModel:
    return MtblTeamRosterModel(
        league_id=1,
        season_id=2025,
        team_id=team_id,
        team_name=f"Team {team_id}",
        team_abbrev=f"T{team_id}",
        primary_owner="owner",
    )


def test_save_team_roster_creates_file(tmp_path):
    roster = _make_team_roster(team_id=1)
    file_path = league_output.save_team_roster(roster, str(tmp_path))

    assert file_path.exists()
    assert file_path.name == "team_1_roster.json"

    with open(file_path, "r") as f:
        data = json.load(f)
    assert data["team_id"] == 1
    assert data["team_name"] == "Team 1"


def test_save_all_team_rosters_returns_paths(tmp_path):
    rosters = [_make_team_roster(team_id=1), _make_team_roster(team_id=2)]
    saved = league_output.save_all_team_rosters(rosters, str(tmp_path))

    assert len(saved) == 2
    assert all(isinstance(path, Path) for path in saved)
    assert (tmp_path / "team_1_roster.json").exists()
    assert (tmp_path / "team_2_roster.json").exists()


def test_save_league_summary_creates_file(tmp_path):
    summary = MtblLeagueModel(
        league_id=10,
        season_id=2025,
        num_teams=2,
    )
    file_path = league_output.save_league_summary(summary, str(tmp_path))

    assert file_path.exists()
    assert file_path.name == "league_10_summary.json"

    with open(file_path, "r") as f:
        data = json.load(f)
    assert data["league_id"] == 10
    assert data["num_teams"] == 2


def test_save_schedule_creates_file(tmp_path):
    schedule = MtblScheduleModel(
        league_id=20,
        season_id=2025,
        matchups=[],
    )
    file_path = league_output.save_schedule(schedule, str(tmp_path))

    assert file_path.exists()
    assert file_path.name == "league_20_schedule.json"

    with open(file_path, "r") as f:
        data = json.load(f)
    assert data["league_id"] == 20
    assert data["matchups"] == []


def test_save_league_results_with_schedule(tmp_path):
    summary = MtblLeagueModel(
        league_id=1,
        season_id=2025,
        num_teams=2,
    )
    rosters = [_make_team_roster(team_id=1), _make_team_roster(team_id=2)]
    schedule = MtblScheduleModel(
        league_id=1,
        season_id=2025,
        matchups=[],
    )

    result = league_output.save_league_results(
        summary, rosters, str(tmp_path), schedule=schedule
    )

    assert result["num_teams"] == 2
    assert Path(result["league_file"]).exists()
    assert Path(result["schedule_file"]).exists()
    assert len(result["team_files"]) == 2


def test_save_league_results_without_schedule(tmp_path):
    summary = MtblLeagueModel(
        league_id=1,
        season_id=2025,
        num_teams=1,
    )
    rosters = [_make_team_roster(team_id=1)]

    result = league_output.save_league_results(summary, rosters, str(tmp_path))

    assert result["num_teams"] == 1
    assert "schedule_file" not in result
