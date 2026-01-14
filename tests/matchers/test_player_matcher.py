from player_universe_trx.matchers.player_matcher import (
    ESPN_TO_FG_TEAM_MAPPING,
    PlayerMatcher,
)
from player_universe_trx.matchers.transformation import apply_matches
from player_universe_trx.models.espn import EspnBatterModel
from player_universe_trx.models.fangraphs import FangraphsBatterModel


def test_match_exact_first_and_last_name(espn_player_data, fangraphs_player_data):
    """Test matching players with exact first and last name match."""
    # Find Corbin Carroll in the ESPN data
    corbin_espn_data = None
    for player in espn_player_data:
        if player.get("name") == "Corbin Carroll":
            corbin_espn_data = player
            break

    assert corbin_espn_data is not None, "Couldn't find Corbin Carroll in ESPN data"

    # Find Corbin Carroll in the FanGraphs data
    corbin_fg_data = None
    for player in fangraphs_player_data:
        if player.get("name") == "Corbin Carroll":
            corbin_fg_data = player
            break

    assert corbin_fg_data is not None, "Couldn't find Corbin Carroll in FanGraphs data"

    # Convert to models
    corbin_espn = EspnBatterModel(
        id=corbin_espn_data["id"],
        name=corbin_espn_data["name"],
        first_name=corbin_espn_data.get("first_name"),
        last_name=corbin_espn_data.get("last_name"),
        slug=corbin_espn_data.get("slug"),
        pro_team=corbin_espn_data.get("pro_team"),
    )
    corbin_fg = FangraphsBatterModel(**corbin_fg_data)

    # Test matching with just these two players
    matcher = PlayerMatcher([corbin_espn], [corbin_fg])
    results = matcher.match_players()
    merged = apply_matches(results)

    assert len(merged["matched"]) == 1
    assert len(merged["ambiguous"]) == 0
    assert len(merged["unmatched"]) == 0
    matched_player = merged["matched"][0]
    assert matched_player.id_fangraphs == corbin_fg_data["playerid"]


def test_match_with_multiple_players_same_last_name(
    espn_player_data, fangraphs_player_data
):
    """Test matching when multiple players have the same last name."""
    # Create test data with multiple players named "Smith"
    smith1 = EspnBatterModel(
        id=1001,
        name="John Smith",
        first_name="John",
        last_name="Smith",
        pro_team="NYY",
    )

    smith2 = EspnBatterModel(
        id=1002,
        name="Mike Smith",
        first_name="Mike",
        last_name="Smith",
        pro_team="LAD",
    )

    fg_smith1 = FangraphsBatterModel(
        playerid="12345", name="John Smith", ascii_name="John Smith", team="NYY"
    )

    fg_smith2 = FangraphsBatterModel(
        playerid="67890", name="Mike Smith", ascii_name="Mike Smith", team="LAD"
    )

    matcher = PlayerMatcher([smith1, smith2], [fg_smith1, fg_smith2])
    results = matcher.match_players()
    merged = apply_matches(results)

    assert len(merged["matched"]) == 2
    smith1_matched = [p for p in merged["matched"] if p.id_espn == 1001][0]
    smith2_matched = [p for p in merged["matched"] if p.id_espn == 1002][0]
    assert smith1_matched.id_fangraphs == "12345"
    assert smith2_matched.id_fangraphs == "67890"


def test_match_with_team_mapping(espn_player_data, fangraphs_player_data):
    """Test matching using team mapping when team codes differ."""
    # Create test data
    player = EspnBatterModel(
        id=1001,
        name="John Smith",
        first_name="John",
        last_name="Smith",
        pro_team="KC",
    )

    fg_player = FangraphsBatterModel(
        playerid="12345", name="John Smith", ascii_name="John Smith", team="KCR"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()
    merged = apply_matches(results)

    assert len(merged["matched"]) == 1
    matched_player = merged["matched"][0]
    assert matched_player.id_fangraphs == "12345"


def test_no_match_found(espn_player_data, fangraphs_player_data):
    """Test handling of players with no matches."""
    # Create test data
    player = EspnBatterModel(
        id=1001,
        name="Unique Player",
        first_name="Unique",
        last_name="Player",
        pro_team="NYY",
    )

    fg_players = [FangraphsBatterModel(**fg_data) for fg_data in fangraphs_player_data]

    matcher = PlayerMatcher([player], fg_players)
    results = matcher.match_players()
    merged = apply_matches(results)

    assert len(merged["unmatched"]) == 1
    unmatched_player = merged["unmatched"][0]
    assert unmatched_player.id_espn == 1001


def test_multiple_matches_scenario(espn_player_data, fangraphs_player_data):
    """Test handling of players with multiple potential matches."""
    # Create test data with two identical players on different teams
    player = EspnBatterModel(
        id=1001,
        name="John Smith",
        first_name="John",
        last_name="Smith",
        pro_team=None,  # No team info
    )

    fg_player1 = FangraphsBatterModel(
        playerid="12345", name="John Smith", ascii_name="John Smith", team="NYA"
    )

    fg_player2 = FangraphsBatterModel(
        playerid="67890", name="John Smith", ascii_name="John Smith", team="BOS"
    )

    matcher = PlayerMatcher([player], [fg_player1, fg_player2])
    results = matcher.match_players()
    merged = apply_matches(results)

    assert len(merged["ambiguous"]) == 1
    ambiguous_tuple = merged["ambiguous"][0]
    assert len(ambiguous_tuple[1]) == 2  # Two candidate matches


def test_matching_players_with_suffixes(espn_player_data, fangraphs_player_data):
    """Test matching players with name suffixes like Jr. or Sr."""
    # Create test data
    junior = EspnBatterModel(
        id=1001,
        name="Ken Griffey Jr.",
        first_name="Ken",
        last_name="Griffey Jr.",
        pro_team="SEA",
    )

    fg_junior = FangraphsBatterModel(
        playerid="12345",
        name="Ken Griffey Jr.",
        ascii_name="Ken Griffey Jr.",
        team="SEA",
    )

    matcher = PlayerMatcher([junior], [fg_junior])
    results = matcher.match_players()
    merged = apply_matches(results)

    assert len(merged["matched"]) == 1
    matched_player = merged["matched"][0]
    assert matched_player.id_fangraphs == "12345"


def test_built_in_team_mapping():
    """Test that the built-in ESPN to FanGraphs team mapping works correctly."""
    assert ESPN_TO_FG_TEAM_MAPPING["KC"] == "KCR"
    assert ESPN_TO_FG_TEAM_MAPPING["SF"] == "SFG"
    assert "SD" in ESPN_TO_FG_TEAM_MAPPING
    assert "TB" in ESPN_TO_FG_TEAM_MAPPING
