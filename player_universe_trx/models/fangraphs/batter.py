from typing import Optional

from player_universe_trx.models.fangraphs.fangraphs_player import FangraphsPlayerModel
from player_universe_trx.models.fangraphs.stats import FangraphsBatterStatsModel


class FangraphsBatterModel(FangraphsPlayerModel):
    """FanGraphs batter model with batter-specific projection statistics."""

    projection: Optional[FangraphsBatterStatsModel] = None
