from typing import Literal, Optional

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import SavantPitcherStatsModel


class SavantPitcherModel(SavantPlayerModel):
    """Savant pitcher model with per-split pitcher statistics.

    Savant emits one row per (player, opp_hand). The consolidator groups those
    rows into three split fields here:
      - all:  overall stats (guaranteed present post-min_pas-filter fix)
      - vs_r: stats facing right-handed batters (None if no sample)
      - vs_l: stats facing left-handed batters (None if no sample)
    """

    player_type: Literal["pitcher"] = "pitcher"
    all: Optional[SavantPitcherStatsModel] = None
    vs_r: Optional[SavantPitcherStatsModel] = None
    vs_l: Optional[SavantPitcherStatsModel] = None
