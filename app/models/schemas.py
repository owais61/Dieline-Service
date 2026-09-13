from pydantic import BaseModel, Field
from typing import Optional


class DielineRequest(BaseModel):
    """
    Request payload for generating a single box dieline.
    length, width, depth are required. Flap dimensions are optional -
    sensible defaults are used when omitted (see ReverseTuckBox).
    """
    length: float = Field(..., gt=0, description="Box length (L) in mm")
    width: float = Field(..., gt=0, description="Box width (W) in mm")
    depth: float = Field(..., gt=0, description="Box depth/height (D) in mm")

    glue_flap: Optional[float] = Field(None, gt=0, description="Glue flap width in mm")
    tuck_flap_depth: Optional[float] = Field(None, gt=0, description="Top/bottom tuck flap depth in mm")
    dust_flap_depth: Optional[float] = Field(None, gt=0, description="Side dust flap depth in mm")

    class Config:
        json_schema_extra = {
            "example": {
                "length": 70,
                "width": 40,
                "depth": 110
            }
        }


class SheetLayoutRequest(DielineRequest):
    """
    Extends DielineRequest with sheet dimensions, used to calculate how
    many boxes fit on a sheet and to render the full multi-box layout.
    """
    sheet_width: float = Field(..., gt=0, description="Sheet width")
    sheet_height: float = Field(..., gt=0, description="Sheet height")
    unit: str = Field("mm", description="Unit for sheet dimensions: 'mm' or 'inch'")
    margin: float = Field(5.0, ge=0, description="Safety margin at sheet edges, in mm")

    class Config:
        json_schema_extra = {
            "example": {
                "length": 70,
                "width": 40,
                "depth": 110,
                "sheet_width": 25,
                "sheet_height": 36,
                "unit": "inch",
                "margin": 5
            }
        }
