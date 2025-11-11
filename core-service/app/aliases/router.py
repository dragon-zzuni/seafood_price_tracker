"""별칭 관련 API 엔드포인트"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.aliases.service import AliasService
from app.aliases.schemas import (
    AliasMatchRequest,
    AliasMatchResponse,
    AliasCreateRequest
)


router = APIRouter(prefix="/aliases", tags=["aliases"])


@router.post("/match", response_model=AliasMatchResponse)
async def match_alias(
    request: AliasMatchRequest,
    db: Session = Depends(get_db)
):
    """
    품목명 매칭 API
    
    원본 품목명(시장에서 수집한 이름)을 표준 Item ID로 매핑합니다.
    
    - **raw_name**: 원본 품목명
    - **market_id**: 시장 ID
    """
    service = AliasService(db)
    return service.match_item(request.raw_name, request.market_id)


@router.post("/", status_code=201)
async def create_alias(
    request: AliasCreateRequest,
    db: Session = Depends(get_db)
):
    """
    새로운 별칭 추가 API (관리자용)
    
    - **item_id**: 품목 ID
    - **market_id**: 시장 ID
    - **raw_name**: 원본 품목명
    - **confidence**: 매칭 신뢰도 (0.0 ~ 1.0)
    """
    service = AliasService(db)
    success = service.add_alias(
        item_id=request.item_id,
        market_id=request.market_id,
        raw_name=request.raw_name,
        confidence=request.confidence
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="별칭 추가에 실패했습니다 (중복 또는 오류)"
        )
    
    return {"message": "별칭이 추가되었습니다"}
