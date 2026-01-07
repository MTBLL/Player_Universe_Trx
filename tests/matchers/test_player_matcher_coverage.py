"""Additional tests to achieve 100% coverage of player_matcher.py."""

from player_universe_trx.matchers.player_matcher import (
    PlayerMatcher,
    apply_matches,
    MatchMethod,
    MatchConfidence,
)
from player_universe_trx.models.espn import EspnBatterModel, EspnPitcherModel
from player_universe_trx.models.espn.batter import EspnBatterStats
from player_universe_trx.models.espn.pitcher import EspnPitcherStats
from player_universe_trx.models.espn.stats import EspnBatterStatsModel, EspnPitcherStatsModel
from player_universe_trx.models.fangraphs import FangraphsBatterModel, FangraphsPitcherModel
from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel


def test_slug_match_with_already_matched_player():
    """Test that slug matching skips already matched players."""
    # Create two ESPN players with same slug (edge case)
    player1 = EspnBatterModel(
        id=1,
        name="Player One",
        first_name="Player",
        last_name="One",
        slug="test-player",
        pro_team="NYY"
    )

    player2 = EspnBatterModel(
        id=2,
        name="Player Two",
        first_name="Player",
        last_name="Two",
        slug="test-player",
        pro_team="NYY"
    )

    # FanGraphs player
    fg_player = FangraphsBatterModel(
        playerid="123",
        name="Player One",
        ascii_name="Player One",
        slug="test-player",
        team="NYY"
    )

    matcher = PlayerMatcher([player1, player2], [fg_player])
    results = matcher.match_players()

    # First player should match
    assert results[0].fangraphs_match == fg_player
    assert results[0].match_method == MatchMethod.SLUG

    # Second player should not match (already matched)
    assert results[1].fangraphs_match is None


def test_savant_match_already_matched():
    """Test that Savant matching skips already matched Savant players."""
    # Two ESPN players that could match same Savant player
    player1 = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY"
    )

    player2 = EspnBatterModel(
        id=2,
        name="Aaron Judge Jr",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge-jr",
        pro_team="NYY"
    )

    # FanGraphs players
    fg_judge = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
        xmlbam_id=592450
    )

    fg_judge_jr = FangraphsBatterModel(
        playerid="99999",
        name="Aaron Judge Jr",
        ascii_name="Aaron Judge Jr",
        slug="aaron-judge-jr",
        team="NYY",
        xmlbam_id=592450  # Same xmlbam_id (edge case)
    )

    # Savant player
    savant_judge = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0
    )

    matcher = PlayerMatcher([player1, player2], [fg_judge, fg_judge_jr], [savant_judge])
    results = matcher.match_players()

    # First player gets Savant match
    assert results[0].savant_match == savant_judge

    # Second player doesn't get Savant match (already matched)
    assert results[1].savant_match is None


def test_prefix_name_matching_single_match():
    """Test prefix name matching with single match."""
    player = EspnBatterModel(
        id=1,
        name="Rob Refsnyder",
        first_name="Rob",
        last_name="Refsnyder",
        pro_team="BOS"
    )

    # FanGraphs has full first name
    fg_player = FangraphsBatterModel(
        playerid="10531",
        name="Robert Refsnyder",
        ascii_name="Robert Refsnyder",
        team="BOS"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match == fg_player
    assert results[0].match_method == MatchMethod.PREFIX_NAME
    assert results[0].confidence == MatchConfidence.LOW


def test_prefix_name_matching_with_team_disambiguation():
    """Test prefix name matching with multiple candidates disambiguated by team."""
    player = EspnBatterModel(
        id=1,
        name="Rob Smithson",
        first_name="Rob",
        last_name="Smithson",
        pro_team="NYY"
    )

    # Multiple FanGraphs players with prefix match (Robert starts with Rob)
    fg_robert_nyy = FangraphsBatterModel(
        playerid="1",
        name="Robert Smithson",
        ascii_name="Robert Smithson",
        team="NYY"
    )

    fg_robert_bos = FangraphsBatterModel(
        playerid="2",
        name="Robert Smithson",
        ascii_name="Robert Smithson",
        team="BOS"
    )

    matcher = PlayerMatcher([player], [fg_robert_nyy, fg_robert_bos])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match == fg_robert_nyy
    assert results[0].match_method == MatchMethod.PREFIX_NAME
    assert results[0].confidence == MatchConfidence.MEDIUM  # Prefix + team


def test_prefix_name_matching_ambiguous():
    """Test prefix name matching with ambiguous results."""
    player = EspnBatterModel(
        id=1,
        name="Mike Smith",
        first_name="Mike",
        last_name="Smith",
        pro_team="LAD"  # Different team
    )

    # Multiple FanGraphs players with prefix match, same team
    fg_michael1 = FangraphsBatterModel(
        playerid="1",
        name="Michael Smith",
        ascii_name="Michael Smith",
        team="NYY"
    )

    fg_michael2 = FangraphsBatterModel(
        playerid="2",
        name="Michael Smith",
        ascii_name="Michael Smith",
        team="BOS"
    )

    matcher = PlayerMatcher([player], [fg_michael1, fg_michael2])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match is None
    assert results[0].confidence == MatchConfidence.AMBIGUOUS
    assert len(results[0].candidates) == 2


def test_team_only_matching_single():
    """Test team-only matching (last resort) with single match."""
    player = EspnBatterModel(
        id=1,
        name="Unknown Player",
        first_name="Unknown",
        last_name="Player",
        pro_team="NYY"
    )

    # FanGraphs player with completely different name but same team
    fg_player = FangraphsBatterModel(
        playerid="999",
        name="Different Player",
        ascii_name="Different Player",
        team="NYY"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match == fg_player
    assert results[0].match_method == MatchMethod.TEAM
    assert results[0].confidence == MatchConfidence.LOW


def test_team_only_matching_ambiguous():
    """Test team-only matching with multiple team matches."""
    player = EspnBatterModel(
        id=1,
        name="Unknown Playerson",
        first_name="Unknown",
        last_name="Playerson",
        pro_team="NYY"
    )

    # Multiple FanGraphs players with same last name, same team (ambiguous)
    fg_player1 = FangraphsBatterModel(
        playerid="1",
        name="John Playerson",
        ascii_name="John Playerson",
        team="NYY"
    )

    fg_player2 = FangraphsBatterModel(
        playerid="2",
        name="Mike Playerson",
        ascii_name="Mike Playerson",
        team="NYY"
    )

    matcher = PlayerMatcher([player], [fg_player1, fg_player2])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match is None
    assert results[0].match_method == MatchMethod.TEAM
    assert results[0].confidence == MatchConfidence.AMBIGUOUS


def test_no_match_no_candidates():
    """Test when there are candidates but no team match."""
    player = EspnBatterModel(
        id=1,
        name="John Smith",
        first_name="John",
        last_name="Smith",
        pro_team="LAD"
    )

    # FanGraphs player with same last name but different team
    fg_player = FangraphsBatterModel(
        playerid="1",
        name="Mike Smith",
        ascii_name="Mike Smith",
        team="NYY"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match is None
    assert results[0].confidence == MatchConfidence.AMBIGUOUS
    assert len(results[0].candidates) == 1


def test_exact_name_with_team_disambiguation():
    """Test exact name match with team disambiguation."""
    player = EspnBatterModel(
        id=1,
        name="Mike Trout",
        first_name="Mike",
        last_name="Trout",
        pro_team="LAA"
    )

    # Two Mike Trouts on different teams (edge case)
    fg_trout_laa = FangraphsBatterModel(
        playerid="10155",
        name="Mike Trout",
        ascii_name="Mike Trout",
        team="LAA"
    )

    fg_trout_nyy = FangraphsBatterModel(
        playerid="99999",
        name="Mike Trout",
        ascii_name="Mike Trout",
        team="NYY"
    )

    matcher = PlayerMatcher([player], [fg_trout_laa, fg_trout_nyy])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match == fg_trout_laa
    assert results[0].match_method == MatchMethod.EXACT_NAME
    assert results[0].confidence == MatchConfidence.HIGH  # Name + team


def test_empty_name_handling():
    """Test handling of empty/None names in extraction methods."""
    # Test with empty first name
    player = EspnBatterModel(
        id=1,
        name="Smith",
        first_name="",
        last_name="Smith",
        pro_team="NYY"
    )

    fg_player = FangraphsBatterModel(
        playerid="1",
        name="Smith",
        ascii_name="Smith",
        team="NYY"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()

    # Should still match by last name + team
    assert len(results) == 1
    assert results[0].fangraphs_match == fg_player


def test_filter_by_team_with_espn_mapping():
    """Test team filtering with ESPN to FanGraphs team code mapping."""
    player = EspnBatterModel(
        id=1,
        name="Player One",
        first_name="Player",
        last_name="One",
        pro_team="KC"  # ESPN code
    )

    # FanGraphs uses KCR
    fg_player = FangraphsBatterModel(
        playerid="123",
        name="Player One",
        ascii_name="Player One",
        team="KCR"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match == fg_player


def test_static_method_extract_last_name_empty():
    """Test _extract_last_name with empty string."""
    assert PlayerMatcher._extract_last_name("") == ""
    assert PlayerMatcher._extract_last_name(None) == ""


def test_static_method_extract_first_name_empty():
    """Test _extract_first_name with empty string."""
    assert PlayerMatcher._extract_first_name("") == ""
    assert PlayerMatcher._extract_first_name(None) == ""


def test_no_last_name_no_candidates():
    """Test matching when player has no last name."""
    player = EspnBatterModel(
        id=1,
        name="SingleName",
        first_name="SingleName",
        last_name="",
        pro_team="NYY"
    )

    fg_player = FangraphsBatterModel(
        playerid="123",
        name="John Smith",
        ascii_name="John Smith",
        team="NYY"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match is None
    assert results[0].confidence == MatchConfidence.NONE


def test_prefix_match_reverse_direction():
    """Test prefix matching where FG name is shorter than ESPN name."""
    player = EspnBatterModel(
        id=1,
        name="Christopher Smith",
        first_name="Christopher",
        last_name="Smith",
        pro_team="NYY"
    )

    # FanGraphs has shortened name
    fg_player = FangraphsBatterModel(
        playerid="123",
        name="Chris Smith",
        ascii_name="Chris Smith",
        team="NYY"
    )

    matcher = PlayerMatcher([player], [fg_player])
    results = matcher.match_players()

    assert len(results) == 1
    assert results[0].fangraphs_match == fg_player
    assert results[0].match_method == MatchMethod.PREFIX_NAME

def test_apply_matches_espn_stats_batters_matched():
    """Test apply_matches with ESPN stats for matched batters (covers lines 806-809)."""
    from player_universe_trx.matchers.player_matcher import apply_matches

    espn_player = EspnBatterModel(
        id=1,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(AB=500, H=150, HR=30)
        )
    )

    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    assert len(matched) == 1
    # Verify ESPN current season stats are at top level
    assert matched[0].stats.AB == 500
    assert matched[0].stats.HR == 30


def test_apply_matches_espn_stats_pitchers_matched():
    """Test apply_matches with ESPN stats for matched pitchers (covers lines 832-835)."""
    from player_universe_trx.matchers.player_matcher import apply_matches

    espn_player = EspnPitcherModel(
        id=1,
        name="Gerrit Cole",
        first_name="Gerrit",
        last_name="Cole",
        slug="gerrit-cole",
        pro_team="NYY",
        stats=EspnPitcherStats(
            current_season=EspnPitcherStatsModel(W=15, K=215, ERA=3.15)
        )
    )

    fg_player = FangraphsPitcherModel(
        playerid="13125",
        name="Gerrit Cole",
        ascii_name="Gerrit Cole",
        slug="gerrit-cole",
        team="NYY"
    )

    matcher = PlayerMatcher([espn_player], [fg_player])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    matched = mtbl_players["matched"]
    assert len(matched) == 1
    # Verify ESPN current season stats are at top level
    assert matched[0].stats.W == 15
    assert matched[0].stats.K == 215


def test_apply_matches_espn_stats_batters_unmatched():
    """Test apply_matches with ESPN stats for unmatched batters (covers lines 862-864)."""
    from player_universe_trx.matchers.player_matcher import apply_matches

    espn_player = EspnBatterModel(
        id=1,
        name="Unknown Player",
        first_name="Unknown",
        last_name="Player",
        slug="unknown-player",
        pro_team="NYY",
        stats=EspnBatterStats(
            current_season=EspnBatterStatsModel(AB=100, H=25, HR=5)
        )
    )

    matcher = PlayerMatcher([espn_player], [], [])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    unmatched = mtbl_players["unmatched"]
    assert len(unmatched) == 1
    # Verify ESPN current season stats are at top level
    assert unmatched[0].stats.AB == 100
    assert unmatched[0].stats.HR == 5


def test_apply_matches_espn_stats_pitchers_unmatched():
    """Test apply_matches with ESPN stats for unmatched pitchers (covers lines 872-874)."""
    from player_universe_trx.matchers.player_matcher import apply_matches

    espn_player = EspnPitcherModel(
        id=1,
        name="Unknown Pitcher",
        first_name="Unknown",
        last_name="Pitcher",
        slug="unknown-pitcher",
        pro_team="NYY",
        stats=EspnPitcherStats(
            current_season=EspnPitcherStatsModel(W=5, K=50, ERA=4.50)
        )
    )

    matcher = PlayerMatcher([espn_player], [], [])
    results = matcher.match_players()
    mtbl_players = apply_matches(results)

    unmatched = mtbl_players["unmatched"]
    assert len(unmatched) == 1
    # Verify ESPN current season stats are at top level
    assert unmatched[0].stats.W == 5
    assert unmatched[0].stats.K == 50
