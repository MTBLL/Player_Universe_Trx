from typing import Optional

from pydantic import Field

from player_universe_trx.models.fangraphs.fangraphs_player import FangraphsPlayerModel
from player_universe_trx.models.fangraphs.stats import FangraphsPitcherStatsModel


class FangraphsPitcherModel(FangraphsPlayerModel):
    """FanGraphs pitcher model with pitcher-specific projection statistics."""

    projections: Optional[FangraphsPitcherStatsModel] = Field(
        default=None, alias="projection"
    )
