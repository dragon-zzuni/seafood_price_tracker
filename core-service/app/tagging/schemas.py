"""가격 태깅 관련 스키마"""
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from enum import Enum

class PriceTag(str, Enum):
    """가격 태그"""
    HIGH = "높음"
    NORMAL = "보통"
    LOW = "낮음"

class PriceThresholds(BaseModel):
    """가격 임계값"""
    high_threshold: Decimal = Decimal("1.15")
    low_threshold: Decimal = Decimal("0.90")
    min_days: int = 30

class PriceWithTag(BaseModel):
    """태그가 포함된 가격 정보"""
    item_id: int
    market_id: int
    market_name: str
    price: Decimal
    unit: str
    date: date
    tag: PriceTag
    base_price: Decimal
    ratio: Decimal
    origin: str | None = None
    source: str | None = None
    
    class Config:
        from_attributes = True

class TagCalculationResult(BaseModel):
    """태그 계산 결과"""
    tag: PriceTag
    current_price: Decimal
    base_price: Decimal
    ratio: Decimal
    threshold_high: Decimal
    threshold_low: Decimal
    calculation_period_days: int
    data_points_used: int
