"""시장 리포지토리"""
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import Market
from app.database.base_repository import BaseRepository

class MarketRepository(BaseRepository[Market]):
    """시장 데이터 접근 레이어"""
    
    def __init__(self, db: Session):
        super().__init__(Market, db)
    
    def get_by_code(self, code: str) -> Optional[Market]:
        """시장 코드로 조회"""
        return self.db.query(Market).filter(Market.code == code).first()
    
    def get_by_name(self, name: str) -> Optional[Market]:
        """시장명으로 조회"""
        return self.db.query(Market).filter(Market.name == name).first()
