"""품목 별칭 리포지토리"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import ItemAlias
from app.database.base_repository import BaseRepository

class AliasRepository(BaseRepository[ItemAlias]):
    """품목 별칭 데이터 접근 레이어"""
    
    def __init__(self, db: Session):
        super().__init__(ItemAlias, db)
    
    def find_by_raw_name(self, raw_name: str, market_id: int) -> Optional[ItemAlias]:
        """
        원본 품목명과 시장 ID로 정확히 일치하는 별칭 조회
        """
        return (
            self.db.query(ItemAlias)
            .filter(
                ItemAlias.raw_name == raw_name,
                ItemAlias.market_id == market_id
            )
            .first()
        )
    
    def find_similar(
        self, 
        raw_name: str, 
        threshold: float = 0.85, 
        limit: int = 5
    ) -> List[ItemAlias]:
        """
        유사한 품목명 검색 (Levenshtein distance 기반)
        PostgreSQL의 pg_trgm 확장 필요
        
        참고: 실제 구현 시 pg_trgm 확장을 설치하고
        similarity() 함수를 사용해야 합니다.
        여기서는 ILIKE를 사용한 간단한 구현
        """
        search_pattern = f"%{raw_name}%"
        return (
            self.db.query(ItemAlias)
            .filter(ItemAlias.raw_name.ilike(search_pattern))
            .filter(ItemAlias.confidence >= threshold)
            .limit(limit)
            .all()
        )
    
    def get_by_item_id(self, item_id: int) -> List[ItemAlias]:
        """특정 품목의 모든 별칭 조회"""
        return (
            self.db.query(ItemAlias)
            .filter(ItemAlias.item_id == item_id)
            .all()
        )
    
    def get_by_market_id(self, market_id: int) -> List[ItemAlias]:
        """특정 시장의 모든 별칭 조회"""
        return (
            self.db.query(ItemAlias)
            .filter(ItemAlias.market_id == market_id)
            .all()
        )
    
    def create_or_update(
        self, 
        item_id: int, 
        market_id: int, 
        raw_name: str, 
        confidence: float = 1.0
    ) -> ItemAlias:
        """
        별칭 생성 또는 업데이트
        이미 존재하면 신뢰도만 업데이트
        """
        alias = self.find_by_raw_name(raw_name, market_id)
        if alias:
            alias.confidence = confidence
            self.db.commit()
            self.db.refresh(alias)
        else:
            alias = ItemAlias(
                item_id=item_id,
                market_id=market_id,
                raw_name=raw_name,
                confidence=confidence
            )
            self.db.add(alias)
            self.db.commit()
            self.db.refresh(alias)
        return alias
    
    def get_unmatched_count(self) -> int:
        """매칭되지 않은 별칭 수 (신뢰도가 낮은 것)"""
        return (
            self.db.query(ItemAlias)
            .filter(ItemAlias.confidence < 0.8)
            .count()
        )
