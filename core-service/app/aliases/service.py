"""별칭 관리 서비스"""
from typing import Optional
from sqlalchemy.orm import Session

from app.aliases.matcher import AliasMatcher
from app.aliases.schemas import AliasMatchResponse


class AliasService:
    """별칭 관리 서비스 클래스"""
    
    def __init__(self, db: Session, similarity_threshold: float = 0.85):
        self.db = db
        self.matcher = AliasMatcher(db, similarity_threshold)
    
    def match_item(self, raw_name: str, market_id: int) -> AliasMatchResponse:
        """
        품목명 매칭
        
        Args:
            raw_name: 원본 품목명
            market_id: 시장 ID
            
        Returns:
            매칭 결과
        """
        # 정확한 매칭 시도
        exact_match = self.matcher._find_exact_match(raw_name, market_id)
        if exact_match:
            return AliasMatchResponse(
                item_id=exact_match,
                matched=True,
                match_type="exact"
            )
        
        # 유사도 기반 매칭
        similar_match = self.matcher._find_similar_match(raw_name, market_id)
        if similar_match:
            return AliasMatchResponse(
                item_id=similar_match,
                matched=True,
                match_type="similar"
            )
        
        # 매칭 실패
        return AliasMatchResponse(
            item_id=None,
            matched=False,
            match_type=None
        )
    
    def add_alias(
        self, 
        item_id: int, 
        market_id: int, 
        raw_name: str, 
        confidence: float = 1.0
    ) -> bool:
        """
        새로운 별칭 추가
        
        Args:
            item_id: 품목 ID
            market_id: 시장 ID
            raw_name: 원본 품목명
            confidence: 매칭 신뢰도
            
        Returns:
            성공 여부
        """
        return self.matcher.add_alias(item_id, market_id, raw_name, confidence)
