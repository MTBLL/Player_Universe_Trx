"""Tests for PlayerIndex class."""

from player_universe_trx.matchers.indexing import PlayerIndex
from player_universe_trx.models.fangraphs import FangraphsBatterModel
from player_universe_trx.models.savant import SavantBatterModel


def test_find_by_slug_empty():
    """Test find_by_slug with empty slug."""
    index = PlayerIndex([], [])
    assert index.find_by_slug("") is None
    assert index.find_by_slug(None) is None


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


def test_find_by_slug_no_match():
    """Test find_by_slug when no match exists."""
    fg_player = FangraphsBatterModel(
        name="Test Player",
        playerid="123",
        slug="test-player",
    )
    index = PlayerIndex([fg_player], [])

    # Try with a different slug
    assert index.find_by_slug("different-player") is None


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
