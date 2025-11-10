"""품목 관련 스키마"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal

class ItemBase(BaseModel):
    """품목 기본 스키마"""
    name_ko: str
    name_en: Optional[str] = None
    category: str
    season_start: Optional[int] = None
    season_end: Optional[int] = None
    default_origin: Optional[str] = None
    unit_default: Optional[str] = None

class ItemResponse(ItemBase):
    """품목 응답 스키마"""
    id: int
    
    class Config:
        from_attributes = True

class ItemSearchResponse(BaseModel):
    """품목 검색 응답"""
    items: List[ItemResponse]
    total: int

class SeasonInfo(BaseModel):
    """제철 정보"""
    is_in_season: bool
    season_start: Optional[int] = None
    season_end: Optional[int] = None
    current_month: int

class PriceTrendPoint(BaseModel):
    """가격 추이 데이터 포인트"""
    date: date
    price: Decimal

class PriceTrendData(BaseModel):
    """가격 추이 데이터"""
    market_id: int
    market_name: str
    period_days: int
    data_points: List[PriceTrendPoint]

class PriceWithTagSchema(BaseModel):
    """태그가 포함된 가격 정보"""
    item_id: int
    market_id: int
    market_name: str
    price: Decimal
    unit: str
    date: date
    tag: str  # "높음", "보통", "낮음"
    base_price: Decimal
    ratio: Decimal
    origin: Optional[str] = None
    source: Optional[str] = None

class ItemDashboardResponse(BaseModel):
    """품목 대시보드 통합 응답"""
    # 품목 기본 정보
    item: ItemResponse
    
    # 제철 정보
    season_info: SeasonInfo
    
    # 현재 가격 (태그 포함)
    current_prices: List[PriceWithTagSchema]
    
    # 가격 추이
    price_trends: List[PriceTrendData]
    
    # 데이터 출처
    data_sources: List[str]
    
    # 메타 정보
    query_date: date
