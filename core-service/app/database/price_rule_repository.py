"""가격 규칙 리포지토리"""
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import PriceRule
from app.database.base_repository import BaseRepository

class PriceRuleRepository(BaseRepository[PriceRule]):
    """가격 규칙 데이터 접근 레이어"""
    
    def __init__(self, db: Session):
        super().__init__(PriceRule, db)
    
    def get_by_item_id(self, item_id: int) -> Optional[PriceRule]:
        """품목 ID로 가격 규칙 조회"""
        return (
            self.db.query(PriceRule)
            .filter(PriceRule.item_id == item_id)
            .first()
        )
    
    def get_or_create_default(self, item_id: int) -> PriceRule:
        """
        품목의 가격 규칙 조회, 없으면 기본값으로 생성
        """
        rule = self.get_by_item_id(item_id)
        if not rule:
            rule = PriceRule(
                item_id=item_id,
                high_threshold=1.15,
                low_threshold=0.90,
                min_days=30
            )
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
        return rule
