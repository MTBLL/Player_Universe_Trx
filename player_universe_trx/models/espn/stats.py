from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EspnBatterStatsModel(BaseModel):
    """ESPN batter statistics model."""

    model_config = ConfigDict(populate_by_name=True)

    # Batting statistics
    AB: Optional[float] = Field(default=None, description="At Bats")
    H: Optional[float] = Field(default=None, description="Hits")
    AVG: Optional[float] = Field(default=None, description="Batting Average")
    singles: Optional[float] = Field(default=None, alias="1B", description="Singles")
    doubles: Optional[float] = Field(default=None, alias="2B", description="Doubles")
    triples: Optional[float] = Field(default=None, alias="3B", description="Triples")
    HR: Optional[float] = Field(default=None, description="Home Runs")
    XBH: Optional[float] = Field(default=None, description="Extra Base Hits")
    TB: Optional[float] = Field(default=None, description="Total Bases")
    SLG: Optional[float] = Field(default=None, description="Slugging Percentage")

    # Plate discipline
    B_BB: Optional[float] = Field(default=None, description="Walks (Batter)")
    B_IBB: Optional[float] = Field(default=None, description="Intentional Walks (Batter)")
    HBP: Optional[float] = Field(default=None, description="Hit By Pitch")
    SF: Optional[float] = Field(default=None, description="Sacrifice Flies")
    SAC: Optional[float] = Field(default=None, description="Sacrifices")
    PA: Optional[float] = Field(default=None, description="Plate Appearances")
    OBP: Optional[float] = Field(default=None, description="On Base Percentage")
    OPS: Optional[float] = Field(default=None, description="On Base Plus Slugging")

    # Runs and RBIs
    R: Optional[float] = Field(default=None, description="Runs")
    RBI: Optional[float] = Field(default=None, description="Runs Batted In")

    # Stolen bases
    SB: Optional[float] = Field(default=None, description="Stolen Bases")
    CS: Optional[float] = Field(default=None, description="Caught Stealing")
    SBN: Optional[float] = Field(default=None, description="Stolen Base Net (SB - CS)")

    # Other
    GDP: Optional[float] = Field(default=None, description="Grounded Into Double Play")
    B_SO: Optional[float] = Field(default=None, description="Strikeouts (Batter)")
    G: Optional[float] = Field(default=None, description="Games")

    @model_validator(mode="after")
    def compute_sbn_if_missing(self):
        """Compute SBN from SB - CS when ESPN's payload didn't include it.

        SBN is a derived stat (net steals) that ESPN sometimes omits — we want
        downstream consumers to be able to read SBN unconditionally. The
        compute is non-destructive: if ESPN already supplied SBN, keep it.
        """
        if self.SBN is not None:
            return self
        if self.SB is not None and self.CS is not None:
            self.SBN = self.SB - self.CS
        elif self.SB is not None:
            self.SBN = self.SB
        elif self.CS is not None:
            self.SBN = -self.CS
        return self


class EspnPitcherStatsModel(BaseModel):
    """ESPN pitcher statistics model."""

    model_config = ConfigDict(populate_by_name=True)

    # Pitching statistics
    GP: Optional[float] = Field(default=None, description="Games Pitched")
    GS: Optional[float] = Field(default=None, description="Games Started")
    OUTS: Optional[float] = Field(default=None, description="Outs Recorded")
    TBF: Optional[float] = Field(default=None, description="Total Batters Faced")
    P_H: Optional[float] = Field(default=None, description="Hits Allowed")
    OBA: Optional[float] = Field(default=None, description="Opponent Batting Average")
    P_BB: Optional[float] = Field(default=None, description="Walks Allowed")
    WHIP: Optional[float] = Field(default=None, description="Walks + Hits per Inning Pitched")
    OOBP: Optional[float] = Field(
        default=None, description="Opponent On Base Percentage"
    )
    P_R: Optional[float] = Field(default=None, description="Runs Allowed")
    ER: Optional[float] = Field(default=None, description="Earned Runs")
    P_HR: Optional[float] = Field(default=None, description="Home Runs Allowed")
    ERA: Optional[float] = Field(default=None, description="Earned Run Average")
    K: Optional[float] = Field(default=None, description="Strikeouts (Pitcher)")
    WP: Optional[float] = Field(default=None, description="Wild Pitches")
    W: Optional[float] = Field(default=None, description="Wins")
    L: Optional[float] = Field(default=None, description="Losses")
    WPCT: Optional[float] = Field(default=None, description="Win Percentage")
    QS: Optional[float] = Field(default=None, description="Quality Starts")
    k_bb_ratio: Optional[float] = Field(
        default=None, alias="K/BB", description="Strikeout to Walk Ratio"
    )

    # Relief pitcher statistics
    SV: Optional[float] = Field(default=None, description="Saves")
    HLD: Optional[float] = Field(default=None, description="Holds")
    SVHD: Optional[float] = Field(default=None, description="Saves + Holds")
    SVO: Optional[float] = Field(default=None, description="Save Opportunities")
    BLSV: Optional[float] = Field(default=None, description="Blown Saves")
    SV_pct: Optional[float] = Field(default=None, alias="SV%", description="Save Percentage")

    # Additional statistics
    IP: Optional[float] = Field(default=None, description="Innings Pitched")
    k_per_9: Optional[float] = Field(default=None, alias="K/9", description="Strikeouts per 9 innings")
