"""가격 조회 서비스"""
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database.price_repository import PriceRepository
from app.database.models import MarketPrice, Market
from app.prices.schemas import (
    LatestPriceResponse, 
    PriceTrendResponse, 
    PriceTrendPoint
)

class PriceService:
    """가격 조회 비즈니스 로직"""
    
    def __init__(self, db: Session):
        self.db = db
        self.price_repo = PriceRepository(db)
    
    def get_latest_price(
        self, 
        item_id: int, 
        market_id: int,
        fallback_days: int = 7
    ) -> Optional[LatestPriceResponse]:
        """
        시장별 최신 가격 조회
        
        로직:
        1. 당일 가격 조회 시도
        2. 없으면 최근 7일 이내 데이터 조회
        3. 그래도 없으면 None 반환
        
        Args:
            item_id: 품목 ID
            market_id: 시장 ID
            fallback_days: 대체 데이터 조회 기간 (기본 7일)
        
        Returns:
            LatestPriceResponse 또는 None
        """
        # 1. 당일 가격 조회
        today = date.today()
        price = self.price_repo.get_price_by_date(item_id, market_id, today)
        
        # 2. 당일 데이터가 없으면 최근 N일 이내 조회
        if not price:
            price = self.price_repo.get_latest_price_within_days(
                item_id, 
                market_id, 
                fallback_days
            )
        
        if not price:
            return None
        
        # 시장 정보 조회
        market = self.db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return None
        
        # 응답 생성
        days_old = (today - price.date).days
        return LatestPriceResponse(
            item_id=price.item_id,
            market_id=price.market_id,
            market_name=market.name,
            price=price.price,
            unit=price.unit,
            date=price.date,
            origin=price.origin,
            source=price.source,
            is_today=(days_old == 0),
            days_old=days_old
        )
    
    def get_all_markets_latest_prices(
        self, 
        item_id: int,
        fallback_days: int = 7
    ) -> List[LatestPriceResponse]:
        """
        특정 품목의 모든 시장 최신 가격 조회
        
        Args:
            item_id: 품목 ID
            fallback_days: 대체 데이터 조회 기간
        
        Returns:
            시장별 최신 가격 리스트
        """
        # 모든 시장 조회
        markets = self.db.query(Market).all()
        
        results = []
        for market in markets:
            latest_price = self.get_latest_price(
                item_id, 
                market.id, 
                fallback_days
            )
            if latest_price:
                results.append(latest_price)
        
        return results
    
    def get_price_trend(
        self, 
        item_id: int, 
        market_id: int,
        period_days: int = 30,
        min_data_points: int = 3
    ) -> Optional[PriceTrendResponse]:
        """
        가격 추이 조회
        
        Args:
            item_id: 품목 ID
            market_id: 시장 ID
            period_days: 조회 기간 (일)
            min_data_points: 최소 데이터 포인트 수
        
        Returns:
            PriceTrendResponse 또는 None (데이터 부족 시)
        """
        # 가격 추이 데이터 조회
        prices = self.price_repo.get_price_trend(item_id, market_id, period_days)
        
        # 최소 데이터 포인트 검증
        if len(prices) < min_data_points:
            return None
        
        # 시장 정보 조회
        market = self.db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return None
        
        # 데이터 포인트 변환
        data_points = [
            PriceTrendPoint(date=p.date, price=p.price)
            for p in prices
        ]
        
        return PriceTrendResponse(
            item_id=item_id,
            market_id=market_id,
            market_name=market.name,
            period_days=period_days,
            data_points=data_points,
            data_count=len(data_points)
        )
    
    def get_all_markets_price_trends(
        self, 
        item_id: int,
        period_days: int = 30,
        min_data_points: int = 3
    ) -> List[PriceTrendResponse]:
        """
        특정 품목의 모든 시장 가격 추이 조회
        
        Args:
            item_id: 품목 ID
            period_days: 조회 기간
            min_data_points: 최소 데이터 포인트 수
        
        Returns:
            시장별 가격 추이 리스트
        """
        markets = self.db.query(Market).all()
        
        results = []
        for market in markets:
            trend = self.get_price_trend(
                item_id, 
                market.id, 
                period_days,
                min_data_points
            )
            if trend:
                results.append(trend)
        
        return results
