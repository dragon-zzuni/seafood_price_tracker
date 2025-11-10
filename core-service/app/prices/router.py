"""가격 조회 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.prices.service import PriceService
from app.prices.schemas import LatestPriceResponse, PriceTrendResponse

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/latest/{item_id}/{market_id}", response_model=LatestPriceResponse)
def get_latest_price(
    item_id: int,
    market_id: int,
    fallback_days: int = Query(7, ge=1, le=30, description="대체 데이터 조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    특정 품목과 시장의 최신 가격 조회
    
    - 당일 데이터가 없으면 최근 N일 이내 데이터 반환
    - N일 이내 데이터도 없으면 404 에러
    """
    service = PriceService(db)
    result = service.get_latest_price(item_id, market_id, fallback_days)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"최근 {fallback_days}일 이내 가격 데이터가 없습니다"
        )
    
    return result

@router.get("/latest/{item_id}", response_model=List[LatestPriceResponse])
def get_all_markets_latest_prices(
    item_id: int,
    fallback_days: int = Query(7, ge=1, le=30, description="대체 데이터 조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    특정 품목의 모든 시장 최신 가격 조회
    
    - 각 시장별로 최신 가격 반환
    - 데이터가 없는 시장은 제외
    """
    service = PriceService(db)
    results = service.get_all_markets_latest_prices(item_id, fallback_days)
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="가격 데이터가 없습니다"
        )
    
    return results

@router.get("/trend/{item_id}/{market_id}", response_model=PriceTrendResponse)
def get_price_trend(
    item_id: int,
    market_id: int,
    period_days: int = Query(30, ge=7, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    특정 품목과 시장의 가격 추이 조회
    
    - 지정된 기간의 일별 가격 데이터 반환
    - 최소 3개 이상의 데이터 포인트 필요
    """
    service = PriceService(db)
    result = service.get_price_trend(item_id, market_id, period_days)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="가격 추이 데이터가 부족합니다 (최소 3개 필요)"
        )
    
    return result

@router.get("/trend/{item_id}", response_model=List[PriceTrendResponse])
def get_all_markets_price_trends(
    item_id: int,
    period_days: int = Query(30, ge=7, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    특정 품목의 모든 시장 가격 추이 조회
    
    - 각 시장별 가격 추이 반환
    - 데이터가 부족한 시장은 제외
    """
    service = PriceService(db)
    results = service.get_all_markets_price_trends(item_id, period_days)
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="가격 추이 데이터가 없습니다"
        )
    
    return results
