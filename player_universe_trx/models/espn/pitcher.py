from typing import Optional

from pydantic import BaseModel

from player_universe_trx.models.espn.espn_player import EspnPlayerModel
from player_universe_trx.models.espn.stats import EspnPitcherStatsModel


class EspnPitcherStats(BaseModel):
    """Container for all pitcher stat periods."""

    projections: Optional[EspnPitcherStatsModel] = None
    current_season: Optional[EspnPitcherStatsModel] = None
    previous_season_24: Optional[EspnPitcherStatsModel] = None
    last_7_games: Optional[EspnPitcherStatsModel] = None
    last_15_games: Optional[EspnPitcherStatsModel] = None
    last_30_games: Optional[EspnPitcherStatsModel] = None


class EspnPitcherModel(EspnPlayerModel):
    """ESPN pitcher model with pitcher-specific statistics."""

    stats: Optional[EspnPitcherStats] = None
