from typing import Optional

from pydantic import Field

from player_universe_trx.models.fangraphs.fangraphs_player import FangraphsPlayerModel
from player_universe_trx.models.fangraphs.stats import FangraphsBatterStatsModel


class FangraphsBatterModel(FangraphsPlayerModel):
    """FanGraphs batter model with batter-specific projection statistics."""

    projections: Optional[FangraphsBatterStatsModel] = Field(
        default=None, alias="projection"
    )
