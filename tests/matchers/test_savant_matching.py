"""Tests for Savant data matching via xmlbam_id bridge."""

from player_universe_trx.matchers.player_matcher import (
    MatchMethod,
    PlayerMatcher,
    apply_matches,
)
from player_universe_trx.models.espn import EspnBatterModel
from player_universe_trx.models.fangraphs import FangraphsBatterModel
from player_universe_trx.models.savant import (
    SavantBatterModel,
    SavantBatterStatsModel,
    SavantPlayerModel,
)


def test_savant_match_via_xmlbam_id():
    """Test that Savant data is matched via xmlbam_id from FanGraphs."""
    # ESPN player
    espn_player = EspnBatterModel(
        id=12345,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        slug="aaron-judge",
        pro_team="NYY",
    )

    # FanGraphs player with xmlbam_id
    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        slug="aaron-judge",
        team="NYY",
        xmlbam_id=592450,  # This links to Savant
    )

    # Savant player with matching player_id
    savant_player = SavantBatterModel(
        player_id=592450,  # Matches FG xmlbam_id
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0,
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    assert result.fangraphs_match == fg_player
    assert result.savant_match == savant_player
    assert result.match_method == MatchMethod.SLUG


def test_savant_no_match_when_xmlbam_id_missing():
    """Test that Savant match is None when FanGraphs has no xmlbam_id."""
    # ESPN player
    espn_player = EspnBatterModel(
        id=12345,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        pro_team="NYY",
    )

    # FanGraphs player WITHOUT xmlbam_id
    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        team="NYY",
        # No xmlbam_id field
    )

    # Savant player exists but can't be matched
    savant_player = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0,
        exit_velo=95.4,
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    assert result.fangraphs_match == fg_player
    assert result.savant_match is None  # No Savant match


def test_savant_no_match_when_player_id_not_in_savant():
    """Test that Savant match is None when xmlbam_id doesn't exist in Savant data."""
    # ESPN player
    espn_player = EspnBatterModel(
        id=12345,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        pro_team="NYY",
    )

    # FanGraphs player with xmlbam_id
    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        team="NYY",
        xmlbam_id=592450,
    )

    # Savant has different player (not Judge)
    savant_player = SavantBatterModel(
        player_id=999999,  # Different ID
        name="Other, Player",
        first_name="Other",
        last_name="Player",
        name_ascii="Other Player",
        slug="other-player",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0,
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    assert result.fangraphs_match == fg_player
    assert result.savant_match is None  # No matching Savant data


def test_savant_stats_merged_correctly():
    """Test that Savant stats are properly merged into PlayerModel."""
    # ESPN player
    espn_player = EspnBatterModel(
        id=12345,
        name="Aaron Judge",
        first_name="Aaron",
        last_name="Judge",
        pro_team="NYY",
    )

    # FanGraphs player
    fg_player = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        team="NYY",
        xmlbam_id=592450,
    )

    savant_player = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0,
        stats=SavantBatterStatsModel(
            exit_velo=95.4,
            barrels_per_bbe_pct=15.2,
            hardhit_pct=52.3,
            xwOBA=0.463,
            xAVG=0.312,
            xSLG=0.654,
            swing_miss_pct=22.5,
            bat_speed=75.8,
            attack_angle=12.3,
        ),
    )

    matcher = PlayerMatcher([espn_player], [fg_player], [savant_player])
    results = matcher.match_players()
    merged = apply_matches(results)

    matched_player = merged["matched"][0]

    # Verify Savant stats were merged into stats object
    assert matched_player.stats is not None
    assert matched_player.stats.current_season is not None
    assert matched_player.stats.current_season.exit_velo == 95.4
    assert matched_player.stats.current_season.barrels_per_bbe_pct == 15.2
    assert matched_player.stats.current_season.hardhit_pct == 52.3
    assert matched_player.stats.current_season.xwOBA == 0.463
    assert matched_player.stats.current_season.xAVG == 0.312
    assert matched_player.stats.current_season.xSLG == 0.654
    assert matched_player.stats.current_season.swing_miss_pct == 22.5
    assert matched_player.stats.current_season.bat_speed == 75.8
    assert matched_player.stats.current_season.attack_angle == 12.3


def test_savant_no_data_when_no_fangraphs_match():
    """Test that Savant data is not matched when FanGraphs match fails."""
    # ESPN player
    espn_player = EspnBatterModel(
        id=12345,
        name="Unknown Player",
        first_name="Unknown",
        last_name="Player",
        pro_team="NYY",
    )

    # No FanGraphs data for this player
    fg_players = []

    # Savant player exists
    savant_player = SavantBatterModel(
        player_id=592450,
        name="Someone, Else",
        first_name="Someone",
        last_name="Else",
        name_ascii="Someone Else",
        slug="someone-else",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0,
    )

    matcher = PlayerMatcher([espn_player], fg_players, [savant_player])
    results = matcher.match_players()

    assert len(results) == 1
    result = results[0]
    assert result.fangraphs_match is None
    assert result.savant_match is None  # Can't get Savant without FanGraphs
    assert result.match_method == MatchMethod.NONE


def test_multiple_players_correct_savant_matches():
    """Test that each player gets the correct Savant match."""
    # Two ESPN players
    judge = EspnBatterModel(
        id=1, name="Aaron Judge", first_name="Aaron", last_name="Judge", pro_team="NYY"
    )

    ohtani = EspnBatterModel(
        id=2,
        name="Shohei Ohtani",
        first_name="Shohei",
        last_name="Ohtani",
        pro_team="LAA",
    )

    # FanGraphs data
    fg_judge = FangraphsBatterModel(
        playerid="15640",
        name="Aaron Judge",
        ascii_name="Aaron Judge",
        team="NYY",
        xmlbam_id=592450,
    )

    fg_ohtani = FangraphsBatterModel(
        playerid="19755",
        name="Shohei Ohtani",
        ascii_name="Shohei Ohtani",
        team="LAA",
        xmlbam_id=660271,
    )

    # Savant data
    savant_judge = SavantBatterModel(
        player_id=592450,
        name="Judge, Aaron",
        first_name="Aaron",
        last_name="Judge",
        name_ascii="Aaron Judge",
        slug="aaron-judge",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0,
    )

    savant_ohtani = SavantBatterModel(
        player_id=660271,
        name="Ohtani, Shohei",
        first_name="Shohei",
        last_name="Ohtani",
        name_ascii="Shohei Ohtani",
        slug="shohei-ohtani",
        pitches=1000,
        total_pitches=1000,
        pitch_percent=100.0,
    )

    matcher = PlayerMatcher(
        [judge, ohtani], [fg_judge, fg_ohtani], [savant_judge, savant_ohtani]
    )
    results = matcher.match_players()

    # Judge should match Judge's Savant data
    judge_result = [r for r in results if r.espn_player.name == "Aaron Judge"][0]
    assert judge_result.savant_match == savant_judge
    assert isinstance(judge_result.savant_match, SavantPlayerModel)
    assert judge_result.savant_match.player_id == 592450

    # Ohtani should match Ohtani's Savant data
    ohtani_result = [r for r in results if r.espn_player.name == "Shohei Ohtani"][0]
    assert ohtani_result.savant_match == savant_ohtani
    assert isinstance(ohtani_result.savant_match, SavantPlayerModel)
    assert ohtani_result.savant_match.player_id == 660271
