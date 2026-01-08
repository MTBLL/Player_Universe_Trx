from typing import Optional

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import SavantBatterStatsModel


class SavantBatterModel(SavantPlayerModel):
    """Savant batter model with batter-specific statistics."""

    stats: Optional[SavantBatterStatsModel] = None
