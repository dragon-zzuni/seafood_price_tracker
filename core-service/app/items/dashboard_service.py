"""품목 대시보드 서비스"""
from typing import Optional, List, Set
from datetime import date
from sqlalchemy.orm import Session

from app.database.item_repository import ItemRepository
from app.database.models import Market
from app.tagging.price_evaluator import PriceEvaluator
from app.prices.service import PriceService
from app.items.schemas import (
    ItemDashboardResponse,
    ItemResponse,
    SeasonInfo,
    PriceTrendData,
    PriceWithTagSchema
)
from app.tagging.schemas import PriceWithTag

class DashboardService:
    """품목 대시보드 통합 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.price_service = PriceService(db)
        self.price_evaluator = PriceEvaluator(db)
    
    def _calculate_season_info(
        self, 
        season_start: Optional[int], 
        season_end: Optional[int],
        target_date: date = None
    ) -> SeasonInfo:
        """
        제철 여부 계산
        
        Args:
            season_start: 제철 시작 월 (1-12)
            season_end: 제철 종료 월 (1-12)
            target_date: 기준 날짜 (None이면 오늘)
        
        Returns:
            SeasonInfo
        """
        if target_date is None:
            target_date = date.today()
        
        current_month = target_date.month
        
        # 제철 정보가 없으면 항상 False
        if season_start is None or season_end is None:
            return SeasonInfo(
                is_in_season=False,
                season_start=None,
                season_end=None,
                current_month=current_month
            )
        
        # 제철 기간 판단
        if season_start <= season_end:
            # 일반적인 경우: 3월~5월
            is_in_season = season_start <= current_month <= season_end
        else:
            # 연도를 넘어가는 경우: 11월~2월
            is_in_season = current_month >= season_start or current_month <= season_end
        
        return SeasonInfo(
            is_in_season=is_in_season,
            season_start=season_start,
            season_end=season_end,
            current_month=current_month
        )
    
    def _collect_data_sources(
        self, 
        prices: List[PriceWithTagSchema]
    ) -> List[str]:
        """
        데이터 출처 수집
        
        Args:
            prices: 가격 데이터 리스트
        
        Returns:
            고유한 출처 리스트
        """
        sources: Set[str] = set()
        
        for price in prices:
            if price.source:
                sources.add(price.source)
            # 시장명도 출처로 추가
            sources.add(price.market_name)
        
        return sorted(list(sources))
    
    def get_dashboard(
        self, 
        item_id: int,
        target_date: date = None,
        trend_period_days: int = 30
    ) -> Optional[ItemDashboardResponse]:
        """
        품목 대시보드 데이터 조회
        
        통합 정보:
        1. 품목 기본 정보
        2. 제철 여부
        3. 시장별 현재 가격 + 태그
        4. 시장별 가격 추이
        5. 데이터 출처
        
        Args:
            item_id: 품목 ID
            target_date: 기준 날짜 (None이면 오늘)
            trend_period_days: 가격 추이 조회 기간
        
        Returns:
            ItemDashboardResponse 또는 None
        """
        if target_date is None:
            target_date = date.today()
        
        # 1. 품목 정보 조회
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return None
        
        item_response = ItemResponse.model_validate(item)
        
        # 2. 제철 정보 계산
        season_info = self._calculate_season_info(
            item.season_start,
            item.season_end,
            target_date
        )
        
        # 3. 모든 시장의 현재 가격 + 태그 조회
        markets = self.db.query(Market).all()
        current_prices: List[PriceWithTagSchema] = []
        
        for market in markets:
            price_with_tag = self.price_evaluator.calculate_tag_for_latest_price(
                item_id,
                market.id
            )
            if price_with_tag:
                # PriceWithTag를 PriceWithTagSchema로 변환
                current_prices.append(
                    PriceWithTagSchema(
                        item_id=price_with_tag.item_id,
                        market_id=price_with_tag.market_id,
                        market_name=price_with_tag.market_name,
                        price=price_with_tag.price,
                        unit=price_with_tag.unit,
                        date=price_with_tag.date,
                        tag=price_with_tag.tag.value,  # Enum을 문자열로 변환
                        base_price=price_with_tag.base_price,
                        ratio=price_with_tag.ratio,
                        origin=price_with_tag.origin,
                        source=price_with_tag.source
                    )
                )
        
        # 가격 데이터가 하나도 없으면 None 반환
        if not current_prices:
            return None
        
        # 4. 가격 추이 조회
        price_trends: List[PriceTrendData] = []
        
        for market in markets:
            trend = self.price_service.get_price_trend(
                item_id,
                market.id,
                trend_period_days,
                min_data_points=3
            )
            if trend:
                price_trends.append(
                    PriceTrendData(
                        market_id=trend.market_id,
                        market_name=trend.market_name,
                        period_days=trend.period_days,
                        data_points=trend.data_points
                    )
                )
        
        # 5. 데이터 출처 수집
        data_sources = self._collect_data_sources(current_prices)
        
        return ItemDashboardResponse(
            item=item_response,
            season_info=season_info,
            current_prices=current_prices,
            price_trends=price_trends,
            data_sources=data_sources,
            query_date=target_date
        )
