"""품목 관리 서비스"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database.models import Item
from app.items.schemas import ItemResponse


class ItemService:
    """품목 관리 서비스 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_items(
        self, 
        query: Optional[str] = None, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> list[ItemResponse]:
        """
        품목 검색 (자동완성용)
        
        Args:
            query: 검색어 (품목명)
            category: 카테고리 필터
            limit: 최대 결과 수
            
        Returns:
            검색된 품목 리스트
        """
        db_query = self.db.query(Item)
        
        # 검색어 필터링
        if query:
            search_pattern = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    Item.name_ko.ilike(search_pattern),
                    Item.name_en.ilike(search_pattern)
                )
            )
        
        # 카테고리 필터링
        if category:
            db_query = db_query.filter(Item.category == category)
        
        # 결과 제한 및 정렬 (한글명 기준)
        items = db_query.order_by(Item.name_ko).limit(limit).all()
        
        return [ItemResponse.model_validate(item) for item in items]
    
    def get_item_by_id(self, item_id: int) -> Optional[ItemResponse]:
        """
        품목 ID로 상세 정보 조회
        
        Args:
            item_id: 품목 ID
            
        Returns:
            품목 정보 또는 None
        """
        item = self.db.query(Item).filter(Item.id == item_id).first()
        
        if item:
            return ItemResponse.model_validate(item)
        return None
    
    def get_all_categories(self) -> list[str]:
        """
        모든 카테고리 목록 조회
        
        Returns:
            카테고리 리스트
        """
        categories = self.db.query(Item.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]
