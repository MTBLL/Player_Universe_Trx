from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectionSource(str, Enum):
    STEAMER = "steamer"
    ATC = "atc"
    THE_BAT = "the_bat"
    ZIPS = "zips"
    DEPTH_CHARTS = "depth_charts"


class BaseProjectionModel(BaseModel):
    """Base class for projection data from different sources"""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    # Common projection fields
    season: Optional[str] = Field(None, alias="Season")

    # Percentiles (common across projection systems)
    q10: Optional[float] = None
    q20: Optional[float] = None
    q30: Optional[float] = None
    q40: Optional[float] = None
    q50: Optional[float] = None
    q60: Optional[float] = None
    q70: Optional[float] = None
    q80: Optional[float] = None
    q90: Optional[float] = None
    tt_q10: Optional[float] = None
    tt_q20: Optional[float] = None
    tt_q30: Optional[float] = None
    tt_q40: Optional[float] = None
    tt_q50: Optional[float] = None
    tt_q60: Optional[float] = None
    tt_q70: Optional[float] = None
    tt_q80: Optional[float] = None
    tt_q90: Optional[float] = None

    # Fantasy points (common across projection systems)
    fpts: Optional[float] = Field(None, alias="FPTS")
    fpts_pa: Optional[float] = Field(None, alias="FPTS_PA")
    fpts_ip: Optional[float] = Field(None, alias="FPTS_IP")
    spts: Optional[float] = Field(None, alias="SPTS")
    spts_pa: Optional[float] = Field(None, alias="SPTS_PA")
    spts_ip: Optional[float] = Field(None, alias="SPTS_IP")
