from pydantic import BaseModel, Field, conlist
from typing import Optional, List
from datetime import date
from decimal import Decimal

class ForecastBase(BaseModel):
    symbol: str
    range_days: int
    forecast_date: date
    target_date: date
    model_name: str
    model_version: Optional[str] = None
    model_id: Optional[int] = None

    used_indicators: Optional[List[str]] = Field(default=None)
    feature_importance: Optional[dict] = None

    prediction: Optional[Decimal] = None
    direction: Optional[str] = Field(default=None)  # up|down|neutral
    confidence: Optional[Decimal] = None
    sl_target: Optional[Decimal] = None
    tp_target: Optional[Decimal] = None

class ForecastCreate(ForecastBase):
    pass

class ForecastOut(ForecastBase):
    id: int

class BulkForecastCreate(BaseModel):
    items: conlist(ForecastCreate, min_length=1)
