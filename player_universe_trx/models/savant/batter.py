from typing import Literal, Optional

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import SavantBatterStatsModel


class SavantBatterModel(SavantPlayerModel):
    """Savant batter model with per-split batter statistics.

    Savant emits one row per (player, opp_hand). The consolidator groups those
    rows into three split fields here:
      - all:  overall stats (guaranteed present post-min_pas-filter fix)
      - vs_r: stats facing right-handed pitchers (None if no sample)
      - vs_l: stats facing left-handed pitchers (None if no sample)
    """

    player_type: Literal["batter"] = "batter"
    all: Optional[SavantBatterStatsModel] = None
    vs_r: Optional[SavantBatterStatsModel] = None
    vs_l: Optional[SavantBatterStatsModel] = None
