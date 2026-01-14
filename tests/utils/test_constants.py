from player_universe_trx.utils import constants


def test_constants_values():
    assert constants.DIR_EXTRACT.endswith("/resources/extract")
    assert constants.DIR_TRX.endswith("/resources/transform")
    assert constants.ESPN_PLAYERS == "espn_player_universe.json"
    assert constants.FANGRAPHS_PLAYERS == "fangraph_players.json"
