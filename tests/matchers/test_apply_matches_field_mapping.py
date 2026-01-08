from player_universe_trx.matchers.models import MatchConfidence, MatchMethod, PlayerMatchResult
from player_universe_trx.matchers.transformation import apply_matches
from player_universe_trx.models.espn import EspnBatterModel


def test_apply_matches_maps_fantasy_and_draft_fields():
    espn_player = EspnBatterModel(
        id=1,
        name="Mapped Player",
        first_name="Mapped",
        last_name="Player",
        on_team_id=12,
        draft_auction_value=25.5,
    )
    result = PlayerMatchResult(
        espn_player=espn_player,
        fangraphs_match=None,
        savant_match=None,
        match_method=MatchMethod.NONE,
        confidence=MatchConfidence.NONE,
    )

    output = apply_matches([result])

    assert len(output["unmatched"]) == 1
    player = output["unmatched"][0]
    assert str(player.fantasy_team) == "12"
    assert str(player.draft_value) == "25.5"
