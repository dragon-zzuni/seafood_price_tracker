"""품목 리포지토리"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database.models import Item
from app.database.base_repository import BaseRepository

class ItemRepository(BaseRepository[Item]):
    """품목 데이터 접근 레이어"""
    
    def __init__(self, db: Session):
        super().__init__(Item, db)
    
    def search_by_name(self, query: str, limit: int = 10) -> List[Item]:
        """
        품목명으로 검색 (자동완성용)
        한글명 또는 영문명에서 부분 일치 검색
        """
        search_pattern = f"%{query}%"
        return (
            self.db.query(Item)
            .filter(
                or_(
                    Item.name_ko.ilike(search_pattern),
                    Item.name_en.ilike(search_pattern)
                )
            )
            .limit(limit)
            .all()
        )
    
    def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Item]:
        """카테고리별 품목 조회"""
        return (
            self.db.query(Item)
            .filter(Item.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_name_ko(self, name_ko: str) -> Optional[Item]:
        """한글명으로 정확히 일치하는 품목 조회"""
        return self.db.query(Item).filter(Item.name_ko == name_ko).first()
    
    def get_seasonal_items(self, month: int) -> List[Item]:
        """
        특정 월의 제철 품목 조회
        season_start와 season_end 사이에 해당 월이 포함되는 품목
        """
        # 제철 기간이 연도를 넘어가는 경우 처리 (예: 11월~2월)
        return (
            self.db.query(Item)
            .filter(
                or_(
                    # 일반적인 경우: start <= month <= end
                    (Item.season_start <= month) & (Item.season_end >= month),
                    # 연도를 넘어가는 경우: start > end이고 (month >= start 또는 month <= end)
                    (Item.season_start > Item.season_end) & 
                    ((month >= Item.season_start) | (month <= Item.season_end))
                )
            )
            .all()
        )
    
    def get_all_categories(self) -> List[str]:
        """모든 카테고리 목록 조회"""
        result = self.db.query(Item.category).distinct().all()
        return [row[0] for row in result]
