from typing import Optional

from pydantic import BaseModel

from player_universe_trx.models.espn.espn_player import EspnPlayerModel
from player_universe_trx.models.espn.stats import EspnBatterStatsModel


class EspnBatterStatsGroupModel(BaseModel):
    """Container for all batter stat periods."""

    projections: Optional[EspnBatterStatsModel] = None
    current_season: Optional[EspnBatterStatsModel] = None
    previous_season_24: Optional[EspnBatterStatsModel] = None
    last_7_games: Optional[EspnBatterStatsModel] = None
    last_15_games: Optional[EspnBatterStatsModel] = None
    last_30_games: Optional[EspnBatterStatsModel] = None


class EspnBatterModel(EspnPlayerModel):
    """ESPN batter model with batter-specific statistics."""

    stats: Optional[EspnBatterStatsGroupModel] = None
