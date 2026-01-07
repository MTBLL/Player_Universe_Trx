"""MTBL pitcher model with combined stats from all sources."""

from typing import Optional

from player_universe_trx.models.mtbl.mtbl_player import MtblPlayerModel
from player_universe_trx.models.mtbl.stats import MtblPitcherStatsModel


class MtblPitcherModel(MtblPlayerModel):
    """
    MTBL pitcher model with pitcher-specific statistics.

    Combines player information from MtblPlayerModel with comprehensive pitching statistics
    from ESPN (current), FanGraphs (projections), and Savant (sabermetrics).
    """

    stats: Optional[MtblPitcherStatsModel] = None
