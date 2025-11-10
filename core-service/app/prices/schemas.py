"""가격 관련 스키마"""
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from decimal import Decimal

class PriceBase(BaseModel):
    """가격 기본 스키마"""
    item_id: int
    market_id: int
    date: date
    price: Decimal
    unit: str
    origin: Optional[str] = None
    source: Optional[str] = None

class PriceResponse(PriceBase):
    """가격 응답 스키마"""
    id: int
    market_name: str
    
    class Config:
        from_attributes = True

class PriceTrendPoint(BaseModel):
    """가격 추이 데이터 포인트"""
    date: date
    price: Decimal
    
    class Config:
        from_attributes = True

class PriceTrendResponse(BaseModel):
    """가격 추이 응답"""
    item_id: int
    market_id: int
    market_name: str
    period_days: int
    data_points: List[PriceTrendPoint]
    data_count: int

class LatestPriceResponse(BaseModel):
    """최신 가격 응답"""
    item_id: int
    market_id: int
    market_name: str
    price: Decimal
    unit: str
    date: date
    origin: Optional[str] = None
    source: Optional[str] = None
    is_today: bool
    days_old: int
    
    class Config:
        from_attributes = True
