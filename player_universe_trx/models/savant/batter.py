from typing import Literal, Optional

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import SavantBatterStatsModel


class SavantBatterModel(SavantPlayerModel):
    """Savant batter model with batter-specific statistics."""

    player_type: Literal["batter"] = "batter"
    stats: Optional[SavantBatterStatsModel] = None
