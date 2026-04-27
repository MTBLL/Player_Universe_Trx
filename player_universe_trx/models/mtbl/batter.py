"""MTBL batter model with combined stats from all sources."""

from typing import Literal, Optional

from player_universe_trx.models.mtbl.mtbl_player import MtblPlayerModel
from player_universe_trx.models.mtbl.stats import MtblBatterStatsModel


class MtblBatterModel(MtblPlayerModel):
    """
    MTBL batter model with batter-specific statistics.

    Combines player information from MtblPlayerModel with comprehensive batting statistics
    from ESPN (current), FanGraphs (projections), and Savant (sabermetrics).
    """

    player_type: Literal["batter"] = "batter"
    stats: Optional[MtblBatterStatsModel] = None
