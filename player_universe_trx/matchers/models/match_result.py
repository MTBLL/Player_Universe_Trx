from dataclasses import dataclass, field
from typing import List, Optional

from player_universe_trx.models.espn.batter import EspnBatterModel
from player_universe_trx.models.espn.pitcher import EspnPitcherModel
from player_universe_trx.models.fangraphs.batter import FangraphsBatterModel
from player_universe_trx.models.fangraphs.pitcher import FangraphsPitcherModel
from player_universe_trx.models.savant.batter import SavantBatterModel
from player_universe_trx.models.savant.pitcher import SavantPitcherModel

from .match_confidence import MatchConfidence
from .match_method import MatchMethod


@dataclass
class PlayerMatchResult:
    """
    Result of matching a player across data sources.

    This is a transient object used for auditing and debugging the matching process.
    It is not stored in the PlayerModel, but can be inspected to understand how
    matches were made.
    """

    espn_player: EspnBatterModel | EspnPitcherModel
    fangraphs_match: Optional[FangraphsBatterModel | FangraphsPitcherModel]
    savant_match: Optional[SavantBatterModel | SavantPitcherModel]
    match_method: MatchMethod
    confidence: MatchConfidence
    candidates: List[FangraphsBatterModel | FangraphsPitcherModel] = field(
        default_factory=list
    )
    notes: str = ""
