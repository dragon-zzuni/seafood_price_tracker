"""별칭 관련 스키마 정의"""
from pydantic import BaseModel, Field
from typing import Optional


class AliasBase(BaseModel):
    """별칭 기본 정보"""
    item_id: int
    market_id: int
    raw_name: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class AliasResponse(AliasBase):
    """별칭 응답 모델"""
    id: int
    
    class Config:
        from_attributes = True


class AliasCreateRequest(BaseModel):
    """별칭 생성 요청"""
    item_id: int
    market_id: int
    raw_name: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class AliasMatchRequest(BaseModel):
    """별칭 매칭 요청"""
    raw_name: str
    market_id: int


class AliasMatchResponse(BaseModel):
    """별칭 매칭 응답"""
    item_id: Optional[int] = None
    matched: bool
    match_type: Optional[str] = None  # "exact" or "similar"
