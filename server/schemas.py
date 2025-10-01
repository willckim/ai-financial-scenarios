from pydantic import BaseModel, Field
from typing import Optional, Dict

class Scenario(BaseModel):
    months_ahead: int = Field(default=12, ge=1, le=36)
    rev_growth_m: Optional[float] = None  # 0.02 = 2%/mo
    churn_m: Optional[float] = None
    cac: Optional[float] = None
    marketing_spend: Optional[float] = None
    price: Optional[float] = None
    cogs_pct: Optional[float] = None
    opex_growth_m: Optional[float] = None

class AnalyzeResponse(BaseModel):
    forecast: list[dict]
    summary: str
    key_metrics: Dict[str, float]
