from typing import Literal, Optional

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import SavantPitcherStatsModel


class SavantPitcherModel(SavantPlayerModel):
    """Savant pitcher model with pitcher-specific statistics."""

    player_type: Literal["pitcher"] = "pitcher"
    stats: Optional[SavantPitcherStatsModel] = None
