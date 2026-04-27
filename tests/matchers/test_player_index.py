"""Tests for PlayerIndex class."""

from player_universe_trx.matchers.indexing import PlayerIndex
from player_universe_trx.models.fangraphs import FangraphsBatterModel
from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel


def test_find_by_slug_empty():
    """Test find_by_slug with empty slug."""
    index = PlayerIndex([], [])
    assert index.find_by_slug("") == []
    assert index.find_by_slug(None) == []


def test_find_by_last_name_empty():
    """Test find_by_last_name with empty last name."""
    index = PlayerIndex([], [])
    assert index.find_by_last_name("") == []
    assert index.find_by_last_name(None) == []


def test_find_by_team_empty():
    """Test find_by_team with empty team."""
    index = PlayerIndex([], [])
    assert index.find_by_team("") == []
    assert index.find_by_team(None) == []


def test_find_savant_by_mlb_id_empty():
    """Test find_savant_by_mlb_id with empty/zero mlb_id."""
    index = PlayerIndex([], [])
    assert index.find_savant_by_mlb_id(0) is None
    assert index.find_savant_by_mlb_id(None) is None


def test_find_savant_by_mlb_id_returns_single_match_without_player_type():
    """Test find_savant_by_mlb_id returns a single unambiguous match."""
    batter = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        pitches=100,
        total_pitches=100,
        pitch_percent=100.0,
    )
    index = PlayerIndex([], [batter])

    assert index.find_savant_by_mlb_id(592450) == batter


def test_find_savant_by_mlb_id_role_miss_does_not_return_opposite_role():
    """Test role-specific Savant lookups do not fall back to the opposite role."""
    batter = SavantBatterModel(
        player_id=660271,
        name="Ohtani, Shohei",
        first_name="Shohei",
        last_name="Ohtani",
        name_ascii="Shohei Ohtani",
        slug="shohei-ohtani",
        pitches=100,
        total_pitches=100,
        pitch_percent=100.0,
    )
    pitcher = SavantPitcherModel(
        player_id=543037,
        name="Cole, Gerrit",
        first_name="Gerrit",
        last_name="Cole",
        name_ascii="Gerrit Cole",
        slug="gerrit-cole",
        pitches=100,
        total_pitches=100,
        pitch_percent=100.0,
    )
    index = PlayerIndex([], [batter, pitcher])

    assert index.find_savant_by_mlb_id(660271, "pitcher") is None
    assert index.find_savant_by_mlb_id(543037, "batter") is None


def test_find_by_slug_no_match():
    """Test find_by_slug when no match exists."""
    fg_player = FangraphsBatterModel(
        name="Test Player",
        playerid="123",
        slug="test-player",
    )
    index = PlayerIndex([fg_player], [])

    # Try with a different slug
    assert index.find_by_slug("different-player") == []


def test_find_by_last_name_no_match():
    """Test find_by_last_name when no match exists."""
    fg_player = FangraphsBatterModel(
        name="Test Player",
        playerid="123",
        slug="test-player",
    )
    index = PlayerIndex([fg_player], [])

    # Try with a different last name
    assert index.find_by_last_name("Smith") == []


def test_find_by_team_no_match():
    """Test find_by_team when no match exists."""
    fg_player = FangraphsBatterModel(
        name="Test Player",
        playerid="123",
        slug="test-player",
        team="NYY",
    )
    index = PlayerIndex([fg_player], [])

    # Try with a different team
    assert index.find_by_team("BOS") == []


def test_savant_index_uses_player_type_for_two_way_players():
    """Test two-way player Savant rows do not overwrite each other."""
    batter = SavantBatterModel(
        player_id=660271,
        name="Ohtani, Shohei",
        first_name="Shohei",
        last_name="Ohtani",
        name_ascii="Shohei Ohtani",
        slug="shohei-ohtani",
        pitches=100,
        total_pitches=100,
        pitch_percent=100.0,
    )
    pitcher = SavantPitcherModel(
        player_id=660271,
        name="Ohtani, Shohei",
        first_name="Shohei",
        last_name="Ohtani",
        name_ascii="Shohei Ohtani",
        slug="shohei-ohtani",
        pitches=100,
        total_pitches=100,
        pitch_percent=100.0,
    )

    index = PlayerIndex([], [batter, pitcher])

    assert index.find_savant_by_mlb_id(660271, "batter") == batter
    assert index.find_savant_by_mlb_id(660271, "pitcher") == pitcher
    assert index.find_savant_by_mlb_id(660271) is None
