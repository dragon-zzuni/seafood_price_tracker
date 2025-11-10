"""품목 관련 API 엔드포인트"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database.connection import get_db
from app.items.service import ItemService
from app.items.dashboard_service import DashboardService
from app.items.schemas import ItemResponse, ItemSearchResponse, ItemDashboardResponse


router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=ItemSearchResponse)
async def search_items(
    query: Optional[str] = Query(None, description="검색어 (품목명)"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(10, ge=1, le=50, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """
    품목 검색 API (자동완성용)
    
    - **query**: 검색어 (한글명 또는 영문명)
    - **category**: 카테고리 필터 (fish, shellfish, crustacean 등)
    - **limit**: 최대 결과 수 (기본 10개, 최대 50개)
    """
    service = ItemService(db)
    items = service.search_items(query=query, category=category, limit=limit)
    
    return ItemSearchResponse(
        items=items,
        total=len(items)
    )


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    품목 상세 정보 조회
    
    - **item_id**: 품목 ID
    """
    service = ItemService(db)
    item = service.get_item_by_id(item_id)
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"품목을 찾을 수 없습니다 (ID: {item_id})"
        )
    
    return item


@router.get("/categories/list", response_model=list[str])
async def get_categories(db: Session = Depends(get_db)):
    """
    모든 카테고리 목록 조회
    """
    service = ItemService(db)
    return service.get_all_categories()


@router.get("/{item_id}/dashboard", response_model=ItemDashboardResponse)
async def get_item_dashboard(
    item_id: int,
    target_date: Optional[date] = Query(None, description="기준 날짜 (기본: 오늘)"),
    trend_period_days: int = Query(30, ge=7, le=365, description="가격 추이 조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    품목 대시보드 통합 API
    
    다음 정보를 통합하여 반환:
    - 품목 기본 정보 (이름, 카테고리, 산지 등)
    - 제철 여부
    - 시장별 현재 가격 + 가격 태그 (높음/보통/낮음)
    - 시장별 가격 추이 (지정된 기간)
    - 데이터 출처 정보
    
    **Parameters:**
    - **item_id**: 품목 ID
    - **target_date**: 기준 날짜 (기본값: 오늘)
    - **trend_period_days**: 가격 추이 조회 기간 (기본 30일, 최대 365일)
    
    **Returns:**
    - 품목 대시보드 통합 데이터
    
    **Errors:**
    - 404: 품목을 찾을 수 없거나 가격 데이터가 없음
    """
    service = DashboardService(db)
    dashboard = service.get_dashboard(
        item_id=item_id,
        target_date=target_date,
        trend_period_days=trend_period_days
    )
    
    if not dashboard:
        raise HTTPException(
            status_code=404,
            detail=f"품목 대시보드 데이터를 찾을 수 없습니다 (ID: {item_id})"
        )
    
    return dashboard
