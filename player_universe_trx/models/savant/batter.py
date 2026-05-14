from typing import List, Literal, Optional

from pydantic import Field

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import (
    SavantBatterStatsModel,
    SavantHomeRunsModel,
    SavantPitchArsenalEntryModel,
    SavantSprintSpeedModel,
    SavantStatcastModel,
    SavantSwingTakeModel,
)


class SavantBatterModel(SavantPlayerModel):
    """Savant batter model with per-split splits + auxiliary sub-domains.

    The Savant extractor now emits multiple files per role. They merge by
    player_id into the fields below:
      - all / vs_r / vs_l: swing/take per-handedness splits (multi-row source)
      - statcast: batted-ball quality summary (flat per-player)
      - home_runs: HR-quality metrics (flat per-player)
      - pitch_arsenal: per-pitch-type performance (multi-row → list)
      - sprint_speed: baserunning metrics (flat per-player, batter-only)
      - swing_take: run value by plate region (flat per-player)
    """

    player_type: Literal["batter"] = "batter"
    all: Optional[SavantBatterStatsModel] = None
    vs_r: Optional[SavantBatterStatsModel] = None
    vs_l: Optional[SavantBatterStatsModel] = None

    statcast: Optional[SavantStatcastModel] = None
    home_runs: Optional[SavantHomeRunsModel] = None
    pitch_arsenal: List[SavantPitchArsenalEntryModel] = Field(default_factory=list)
    sprint_speed: Optional[SavantSprintSpeedModel] = None
    swing_take: Optional[SavantSwingTakeModel] = None
