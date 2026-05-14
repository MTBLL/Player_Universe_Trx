import json
from datetime import datetime
from pathlib import Path

import pytest

from player_universe_trx.loaders.file_loader import DataLoader
from tests.conftest import (
    espn_batters_fixture_file,
    espn_pitchers_fixture_file,
    fangraphs_batters_fixture_file,
    fangraphs_pitchers_fixture_file,
)


@pytest.fixture
def fixtures_dir():
    """Fixture providing the path to the test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def temp_dir_with_files(tmp_path):
    """Fixture creating a temporary directory with test files."""
    import time

    test_data = [{"id": 1, "name": "Test Player"}]

    files_ordered = [
        (espn_batters_fixture_file, test_data),
        ("espn_league_10998_2026_20260513_140635.json", test_data),
    ]

    for filename, data in files_ordered:
        file_path = tmp_path / filename
        with open(file_path, "w") as f:
            json.dump(data, f)
        time.sleep(0.01)

    return tmp_path


def test_init_and_default_path(fixtures_dir):
    """Test initialization with custom and default paths."""
    loader = DataLoader(resources_path=str(fixtures_dir), year=2024)
    assert loader.resources_path == fixtures_dir
    assert loader.year == 2024

    loader_default_year = DataLoader(resources_path=str(fixtures_dir))
    assert loader_default_year.year == datetime.now().year

    assert (
        DataLoader.DEFAULT_RESOURCES_PATH
        == "/Users/Shared/BaseballHQ/resources/extract"
    )

    with pytest.raises(ValueError, match="Resources path does not exist"):
        DataLoader(resources_path="/nonexistent/path")


def test_find_latest_file(temp_dir_with_files):
    """Test finding latest file by modification time."""
    loader = DataLoader(resources_path=str(temp_dir_with_files), year=2026)

    result = loader._find_latest_file(r"espn_batters_2026_\d{8}_\d{6}\.json")
    assert isinstance(result, Path)
    assert result.name == espn_batters_fixture_file

    assert loader._find_latest_file(r"nonexistent_\d{8}_\d{6}\.json") is None


def test_extract_timestamp(fixtures_dir):
    """Test timestamp extraction from filenames."""
    loader = DataLoader(resources_path=str(fixtures_dir), year=2026)

    assert loader._extract_timestamp_from_filename("invalid_filename.json") is None
    result = loader._extract_timestamp_from_filename(espn_batters_fixture_file)
    assert result is not None
    assert isinstance(result, datetime)

    # Test invalid timestamp format (has pattern but invalid date)
    assert (
        loader._extract_timestamp_from_filename(
            "espn_batters_2026_99999999_999999.json"
        )
        is None
    )


def test_extract_savant_season(fixtures_dir):
    """Test Savant season extraction from role-specific filenames."""
    loader = DataLoader(resources_path=str(fixtures_dir), year=2026)

    assert (
        loader._extract_savant_season_from_filename(
            "savant_batters_2026_04_24_1245.json"
        )
        == 2026
    )
    assert loader._extract_savant_season_from_filename("invalid_filename.json") is None


def test_get_file_methods(fixtures_dir):
    """Test all get_*_file methods for success and error cases."""
    # All sources are now year-2026 fixtures, so a single loader covers them.
    loader = DataLoader(resources_path=str(fixtures_dir), year=2026)

    assert loader.get_espn_batters_file().name == espn_batters_fixture_file
    assert loader.get_espn_pitchers_file().name == espn_pitchers_fixture_file
    assert (
        loader.get_espn_league_file(league_id=10998).name
        == "espn_league_10998_2026_20260513_140635.json"
    )
    assert "espn_league_" in loader.get_espn_league_file().name

    assert loader.get_fangraphs_batters_file().name == fangraphs_batters_fixture_file
    assert (
        loader.get_fangraphs_pitchers_file().name == fangraphs_pitchers_fixture_file
    )
    assert (
        loader.get_savant_batters_file().name == "savant_batters_2026_05_14_0516.json"
    )
    assert (
        loader.get_savant_pitchers_file().name == "savant_pitchers_2026_05_14_0516.json"
    )

    # Savant sub-domain accessors — each thinly wraps _get_savant_subdomain_file
    # with a different stem. Exercise each to lock in the stem → filename map.
    assert loader.get_savant_statcast_batters_file().name.startswith(
        "savant_statcast_batter_"
    )
    assert loader.get_savant_statcast_pitchers_file().name.startswith(
        "savant_statcast_pitcher_"
    )
    assert loader.get_savant_home_runs_batters_file().name.startswith(
        "savant_home_runs_batter_"
    )
    assert loader.get_savant_home_runs_pitchers_file().name.startswith(
        "savant_home_runs_pitcher_"
    )
    assert loader.get_savant_pitch_arsenal_batters_file().name.startswith(
        "savant_pitch_arsenal_stats_batter_"
    )
    assert loader.get_savant_pitch_arsenal_pitchers_file().name.startswith(
        "savant_pitch_arsenal_stats_pitcher_"
    )
    assert loader.get_savant_sprint_speed_file().name.startswith("savant_sprint_speed_")
    assert loader.get_savant_expected_statistics_pitchers_file().name.startswith(
        "savant_expected_statistics_pitcher_"
    )
    assert loader.get_savant_swing_take_batters_file().name.startswith(
        "savant_swing_take_batter_"
    )
    assert loader.get_savant_swing_take_pitchers_file().name.startswith(
        "savant_swing_take_pitcher_"
    )

    loader_no_files = DataLoader(resources_path=str(fixtures_dir), year=2099)
    with pytest.raises(
        FileNotFoundError, match="No ESPN batters file found for year 2099"
    ):
        loader_no_files.get_espn_batters_file()
    with pytest.raises(
        FileNotFoundError, match="No ESPN pitchers file found for year 2099"
    ):
        loader_no_files.get_espn_pitchers_file()
    with pytest.raises(FileNotFoundError, match="No ESPN league file found"):
        loader_no_files.get_espn_league_file()
    with pytest.raises(FileNotFoundError, match="league 12345"):
        loader_no_files.get_espn_league_file(league_id=12345)
    with pytest.raises(
        FileNotFoundError, match="No FanGraphs batters file found for year 2099"
    ):
        loader_no_files.get_fangraphs_batters_file()
    with pytest.raises(
        FileNotFoundError, match="No FanGraphs pitchers file found for year 2099"
    ):
        loader_no_files.get_fangraphs_pitchers_file()

    # Savant loaders are year-indifferent, so they will find files from any year
    # Test that they succeed even when configured with a year that doesn't match
    assert loader_no_files.get_savant_batters_file().name.startswith("savant_batters_")
    assert loader_no_files.get_savant_pitchers_file().name.startswith(
        "savant_pitchers_"
    )


def test_savant_subdomain_file_not_found(tmp_path):
    """Each Savant sub-domain accessor raises FileNotFoundError when its file is absent."""
    loader = DataLoader(resources_path=str(tmp_path), year=2026)

    with pytest.raises(FileNotFoundError, match="No Savant statcast batters file found"):
        loader.get_savant_statcast_batters_file()


def test_load_methods(fixtures_dir):
    """Test all load_* methods."""
    # All sources are year-2026 now.
    loader = DataLoader(resources_path=str(fixtures_dir), year=2026)

    batters = loader.load_espn_batters()
    assert isinstance(batters, list) and len(batters) > 0

    pitchers = loader.load_espn_pitchers()
    assert isinstance(pitchers, list) and len(pitchers) > 0

    league = loader.load_espn_league(league_id=10998)
    assert isinstance(league, (dict, list))

    league_no_id = loader.load_espn_league()
    assert isinstance(league_no_id, (dict, list))

    fg_batters = loader.load_fangraphs_batters()
    assert isinstance(fg_batters, list) and len(fg_batters) > 0

    fg_pitchers = loader.load_fangraphs_pitchers()
    assert isinstance(fg_pitchers, list) and len(fg_pitchers) > 0

    sv_batters = loader.load_savant_batters()
    assert isinstance(sv_batters, list) and len(sv_batters) > 0
    assert sv_batters[0]["player_type"] == "batter"
    assert sv_batters[0]["season"] == 2026

    sv_pitchers = loader.load_savant_pitchers()
    assert isinstance(sv_pitchers, list) and len(sv_pitchers) > 0
    assert sv_pitchers[0]["player_type"] == "pitcher"
    assert sv_pitchers[0]["season"] == 2026


def test_get_savant_files_not_found(tmp_path):
    """Test Savant file methods raise when no matching files exist."""
    loader = DataLoader(resources_path=str(tmp_path), year=2099)

    with pytest.raises(FileNotFoundError, match="No Savant batters file found"):
        loader.get_savant_batters_file()

    with pytest.raises(FileNotFoundError, match="No Savant pitchers file found"):
        loader.get_savant_pitchers_file()
