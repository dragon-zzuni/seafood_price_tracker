"""가격 리포지토리"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from app.database.models import MarketPrice
from app.database.base_repository import BaseRepository

class PriceRepository(BaseRepository[MarketPrice]):
    """가격 데이터 접근 레이어"""
    
    def __init__(self, db: Session):
        super().__init__(MarketPrice, db)
    
    def get_latest_price(self, item_id: int, market_id: int) -> Optional[MarketPrice]:
        """특정 품목과 시장의 최신 가격 조회"""
        return (
            self.db.query(MarketPrice)
            .filter(
                MarketPrice.item_id == item_id,
                MarketPrice.market_id == market_id
            )
            .order_by(desc(MarketPrice.date))
            .first()
        )
    
    def get_price_by_date(
        self, 
        item_id: int, 
        market_id: int, 
        target_date: date
    ) -> Optional[MarketPrice]:
        """특정 날짜의 가격 조회"""
        return (
            self.db.query(MarketPrice)
            .filter(
                MarketPrice.item_id == item_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date == target_date
            )
            .first()
        )
    
    def get_latest_price_within_days(
        self, 
        item_id: int, 
        market_id: int, 
        days: int = 7
    ) -> Optional[MarketPrice]:
        """
        최근 N일 이내의 최신 가격 조회
        당일 데이터가 없을 때 대체 데이터로 사용
        """
        cutoff_date = date.today() - timedelta(days=days)
        return (
            self.db.query(MarketPrice)
            .filter(
                MarketPrice.item_id == item_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date >= cutoff_date
            )
            .order_by(desc(MarketPrice.date))
            .first()
        )
    
    def get_price_trend(
        self, 
        item_id: int, 
        market_id: int, 
        days: int = 30
    ) -> List[MarketPrice]:
        """
        특정 기간의 가격 추이 조회
        날짜 내림차순 정렬
        """
        cutoff_date = date.today() - timedelta(days=days)
        return (
            self.db.query(MarketPrice)
            .filter(
                MarketPrice.item_id == item_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date >= cutoff_date
            )
            .order_by(MarketPrice.date)
            .all()
        )
    
    def get_average_price(
        self, 
        item_id: int, 
        market_id: int, 
        days: int = 30
    ) -> Optional[float]:
        """
        최근 N일간 평균 가격 계산
        Base Price 계산에 사용
        """
        cutoff_date = date.today() - timedelta(days=days)
        result = (
            self.db.query(func.avg(MarketPrice.price))
            .filter(
                MarketPrice.item_id == item_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date >= cutoff_date
            )
            .scalar()
        )
        return float(result) if result else None
    
    def get_all_markets_latest_prices(self, item_id: int) -> List[MarketPrice]:
        """
        특정 품목의 모든 시장 최신 가격 조회
        대시보드에서 사용
        """
        # 서브쿼리: 각 시장별 최신 날짜
        subquery = (
            self.db.query(
                MarketPrice.market_id,
                func.max(MarketPrice.date).label('max_date')
            )
            .filter(MarketPrice.item_id == item_id)
            .group_by(MarketPrice.market_id)
            .subquery()
        )
        
        # 메인 쿼리: 최신 날짜의 가격 데이터
        return (
            self.db.query(MarketPrice)
            .join(
                subquery,
                and_(
                    MarketPrice.market_id == subquery.c.market_id,
                    MarketPrice.date == subquery.c.max_date
                )
            )
            .filter(MarketPrice.item_id == item_id)
            .all()
        )
    
    def bulk_insert(self, price_dicts: List[dict]) -> int:
        """
        대량 가격 데이터 삽입 (딕셔너리 형태)
        Data Ingestion Service에서 사용
        
        Args:
            price_dicts: 가격 데이터 딕셔너리 리스트
                각 딕셔너리는 item_id, market_id, date, price, unit, origin, source 포함
        
        Returns:
            삽입된 레코드 수
        """
        count = 0
        for price_dict in price_dicts:
            existing = self.get_price_by_date(
                price_dict['item_id'],
                price_dict['market_id'],
                price_dict['date']
            )
            
            if existing:
                # 업데이트
                existing.price = price_dict['price']
                existing.unit = price_dict['unit']
                existing.origin = price_dict.get('origin', '')
                existing.source = price_dict.get('source', '')
            else:
                # 삽입
                new_price = MarketPrice(**price_dict)
                self.db.add(new_price)
            
            count += 1
        
        self.db.commit()
        return count
    
    def bulk_upsert(self, prices: List[MarketPrice]) -> int:
        """
        대량 가격 데이터 삽입/업데이트
        중복 시 업데이트 (ON CONFLICT DO UPDATE)
        """
        count = 0
        for price in prices:
            existing = self.get_price_by_date(
                price.item_id, 
                price.market_id, 
                price.date
            )
            if existing:
                # 업데이트
                existing.price = price.price
                existing.unit = price.unit
                existing.origin = price.origin
                existing.source = price.source
            else:
                # 삽입
                self.db.add(price)
            count += 1
        
        self.db.commit()
        return count
    
    def get_price_count_in_period(
        self, 
        item_id: int, 
        market_id: int, 
        days: int = 30
    ) -> int:
        """특정 기간의 가격 데이터 개수 조회"""
        cutoff_date = date.today() - timedelta(days=days)
        return (
            self.db.query(MarketPrice)
            .filter(
                MarketPrice.item_id == item_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date >= cutoff_date
            )
            .count()
        )
