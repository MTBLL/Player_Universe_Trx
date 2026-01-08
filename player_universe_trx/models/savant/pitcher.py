from typing import Optional

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import SavantPitcherStatsModel


class SavantPitcherModel(SavantPlayerModel):
    """Savant pitcher model with pitcher-specific statistics."""

    stats: Optional[SavantPitcherStatsModel] = None
