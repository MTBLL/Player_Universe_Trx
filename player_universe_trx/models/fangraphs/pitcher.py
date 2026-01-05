from typing import Optional

from player_universe_trx.models.fangraphs.fangraphs_player import FangraphsPlayerModel
from player_universe_trx.models.fangraphs.stats import FangraphsPitcherStatsModel


class FangraphsPitcherModel(FangraphsPlayerModel):
    """FanGraphs pitcher model with pitcher-specific projection statistics."""

    projection: Optional[FangraphsPitcherStatsModel] = None
