from typing import Optional

from pydantic import Field

from player_universe_trx.models.fangraphs.fangraphs_player import FangraphsPlayerModel
from player_universe_trx.models.fangraphs.stats import FangraphsPitcherStatsModel


class FangraphsPitcherModel(FangraphsPlayerModel):
    """FanGraphs pitcher model with the three projection slots emitted by upstream.

    Slots map 1:1 to the Fangraphs extractor's output keys:
      - projections:   canonical preseason mix (only slot with q*/tt_q* percentiles)
      - projs_updated: full-year refit with in-season data ({} until in-season)
      - ros:           rest-of-season ({} until in-season)
    """

    projections: Optional[FangraphsPitcherStatsModel] = Field(default=None)
    projs_updated: Optional[FangraphsPitcherStatsModel] = Field(default=None)
    ros: Optional[FangraphsPitcherStatsModel] = Field(default=None)
