import json
import os
from pathlib import Path

import pytest

from player_universe_trx.loaders.league_loader import LeagueLoader


def _write_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f)


def _league_data(league_id: int, season: int) -> dict:
    return {
        "id": league_id,
        "seasonId": season,
        "teams": [
            {
                "id": 1,
                "name": "Team One",
                "abbrev": "ONE",
                "primaryOwner": "owner1",
                "roster": {"entries": []},
            }
        ],
    }


def test_init_defaults():
    loader = LeagueLoader()
    assert loader.resources_path == LeagueLoader.DEFAULT_RESOURCES_PATH
    assert loader.year is None


def test_init_custom_resources_path():
    loader = LeagueLoader(resources_path="custom/path", year=2025)
    assert loader.resources_path == Path("custom/path")
    assert loader.year == 2025


def test_find_latest_file_selects_most_recent(tmp_path):
    loader = LeagueLoader(resources_path=str(tmp_path), year=2025)
    older = tmp_path / "espn_league_1234_2025_20260102_000000.json"
    newer = tmp_path / "espn_league_1234_2025_20260103_000000.json"
    _write_json(older, _league_data(1234, 2025))
    _write_json(newer, _league_data(1234, 2025))

    os.utime(older, (100, 100))
    os.utime(newer, (200, 200))

    pattern = r"espn_league_1234_2025_\d{8}_\d{6}\.json"
    result = loader._find_latest_file(pattern)
    assert result == newer
    assert loader._find_latest_file(r"nope_\d{8}_\d{6}\.json") is None


def test_get_league_file_with_year(tmp_path):
    loader = LeagueLoader(resources_path=str(tmp_path), year=2025)
    older = tmp_path / "espn_league_2222_2025_20260102_000000.json"
    newer = tmp_path / "espn_league_2222_2025_20260103_000000.json"
    _write_json(older, _league_data(2222, 2025))
    _write_json(newer, _league_data(2222, 2025))
    os.utime(older, (100, 100))
    os.utime(newer, (200, 200))

    assert loader.get_league_file(2222) == newer


def test_get_league_file_without_year(tmp_path):
    loader = LeagueLoader(resources_path=str(tmp_path))
    file_path = tmp_path / "espn_league_3333_2024_20260102_000000.json"
    _write_json(file_path, _league_data(3333, 2024))

    assert loader.get_league_file(3333) == file_path


def test_get_league_file_not_found(tmp_path):
    loader = LeagueLoader(resources_path=str(tmp_path), year=2025)
    with pytest.raises(FileNotFoundError, match="No league file found"):
        loader.get_league_file(9999)


def test_load_league_success(tmp_path):
    loader = LeagueLoader(resources_path=str(tmp_path), year=2025)
    file_path = tmp_path / "espn_league_4444_2025_20260102_000000.json"
    _write_json(file_path, _league_data(4444, 2025))

    league = loader.load_league(4444)
    assert league.id == 4444
    assert len(league.teams) == 1


def test_load_league_invalid_data(tmp_path):
    loader = LeagueLoader(resources_path=str(tmp_path), year=2025)
    file_path = tmp_path / "espn_league_5555_2025_20260102_000000.json"
    _write_json(file_path, {"id": 5555})

    with pytest.raises(ValueError, match="Invalid league data"):
        loader.load_league(5555)
