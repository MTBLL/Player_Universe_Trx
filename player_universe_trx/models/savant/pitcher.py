from typing import List, Literal, Optional

from pydantic import Field

from player_universe_trx.models.savant.savant_player import SavantPlayerModel
from player_universe_trx.models.savant.stats import (
    SavantHomeRunsModel,
    SavantPitcherExpectedStatsModel,
    SavantPitcherStatsModel,
    SavantPitchArsenalEntryModel,
    SavantStatcastModel,
    SavantSwingTakeModel,
)


class SavantPitcherModel(SavantPlayerModel):
    """Savant pitcher model with per-split splits + auxiliary sub-domains.

    The Savant extractor now emits multiple files per role. They merge by
    player_id into the fields below:
      - all / vs_r / vs_l: per-handedness splits (multi-row source)
      - statcast: contact-allowed quality summary (flat per-player)
      - home_runs: HR-allowed quality metrics (flat per-player)
      - pitch_arsenal: per-pitch-type performance (multi-row → list)
      - expected_statistics: xAVG/xSLG/xwOBA/xERA (flat per-player, pitcher-only)
      - swing_take: run value by plate region (flat per-player)
    """

    player_type: Literal["pitcher"] = "pitcher"
    all: Optional[SavantPitcherStatsModel] = None
    vs_r: Optional[SavantPitcherStatsModel] = None
    vs_l: Optional[SavantPitcherStatsModel] = None

    statcast: Optional[SavantStatcastModel] = None
    home_runs: Optional[SavantHomeRunsModel] = None
    pitch_arsenal: List[SavantPitchArsenalEntryModel] = Field(default_factory=list)
    expected_statistics: Optional[SavantPitcherExpectedStatsModel] = None
    swing_take: Optional[SavantSwingTakeModel] = None
