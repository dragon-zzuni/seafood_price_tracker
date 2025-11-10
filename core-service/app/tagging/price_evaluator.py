"""가격 태깅 평가 로직"""
from typing import Optional
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.database.price_repository import PriceRepository
from app.database.price_rule_repository import PriceRuleRepository
from app.database.models import Market
from app.tagging.schemas import (
    PriceTag, 
    PriceThresholds, 
    TagCalculationResult,
    PriceWithTag
)

class PriceEvaluator:
    """
    가격 태깅 계산 로직
    
    최근 30일 평균 가격(Base Price)을 기준으로
    현재 가격이 높음/보통/낮음인지 판단
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.price_repo = PriceRepository(db)
        self.rule_repo = PriceRuleRepository(db)
    
    def _get_thresholds(self, item_id: int) -> PriceThresholds:
        """
        품목별 임계값 조회
        없으면 기본값 사용 (1.15/0.90)
        """
        rule = self.rule_repo.get_by_item_id(item_id)
        
        if rule:
            return PriceThresholds(
                high_threshold=rule.high_threshold,
                low_threshold=rule.low_threshold,
                min_days=rule.min_days
            )
        else:
            # 기본값
            return PriceThresholds()
    
    def _get_base_price(
        self, 
        item_id: int, 
        market_id: int, 
        calculation_days: int
    ) -> Optional[Decimal]:
        """
        Base Price 계산 (최근 N일 평균 가격)
        
        Args:
            item_id: 품목 ID
            market_id: 시장 ID
            calculation_days: 평균 계산 기간
        
        Returns:
            평균 가격 또는 None (데이터 부족 시)
        """
        avg_price = self.price_repo.get_average_price(
            item_id, 
            market_id, 
            calculation_days
        )
        
        if avg_price is None:
            return None
        
        return Decimal(str(avg_price))
    
    def _determine_tag(
        self, 
        current_price: Decimal, 
        base_price: Decimal,
        thresholds: PriceThresholds
    ) -> PriceTag:
        """
        가격 태그 결정
        
        로직:
        - ratio >= high_threshold (1.15) → 높음
        - ratio < low_threshold (0.90) → 낮음
        - 그 외 → 보통
        """
        ratio = current_price / base_price
        
        if ratio >= thresholds.high_threshold:
            return PriceTag.HIGH
        elif ratio < thresholds.low_threshold:
            return PriceTag.LOW
        else:
            return PriceTag.NORMAL
    
    def calculate_tag(
        self, 
        item_id: int, 
        market_id: int,
        current_price: Decimal,
        target_date: date = None
    ) -> Optional[TagCalculationResult]:
        """
        가격 태그 계산
        
        Args:
            item_id: 품목 ID
            market_id: 시장 ID
            current_price: 현재 가격
            target_date: 기준 날짜 (None이면 오늘)
        
        Returns:
            TagCalculationResult 또는 None (데이터 부족 시)
        """
        if target_date is None:
            target_date = date.today()
        
        # 1. 임계값 조회
        thresholds = self._get_thresholds(item_id)
        
        # 2. Base Price 계산
        base_price = self._get_base_price(
            item_id, 
            market_id, 
            thresholds.min_days
        )
        
        if base_price is None or base_price == 0:
            return None
        
        # 3. 태그 결정
        tag = self._determine_tag(current_price, base_price, thresholds)
        
        # 4. 비율 계산
        ratio = current_price / base_price
        
        # 5. 데이터 포인트 수 조회
        data_count = self.price_repo.get_price_count_in_period(
            item_id, 
            market_id, 
            thresholds.min_days
        )
        
        return TagCalculationResult(
            tag=tag,
            current_price=current_price,
            base_price=base_price,
            ratio=ratio,
            threshold_high=thresholds.high_threshold,
            threshold_low=thresholds.low_threshold,
            calculation_period_days=thresholds.min_days,
            data_points_used=data_count
        )
    
    def calculate_tag_for_latest_price(
        self, 
        item_id: int, 
        market_id: int
    ) -> Optional[PriceWithTag]:
        """
        최신 가격에 대한 태그 계산
        
        Args:
            item_id: 품목 ID
            market_id: 시장 ID
        
        Returns:
            PriceWithTag 또는 None
        """
        # 최신 가격 조회
        latest_price = self.price_repo.get_latest_price(item_id, market_id)
        if not latest_price:
            return None
        
        # 태그 계산
        tag_result = self.calculate_tag(
            item_id,
            market_id,
            latest_price.price,
            latest_price.date
        )
        
        if not tag_result:
            return None
        
        # 시장 정보 조회
        market = self.db.query(Market).filter(Market.id == market_id).first()
        if not market:
            return None
        
        return PriceWithTag(
            item_id=item_id,
            market_id=market_id,
            market_name=market.name,
            price=latest_price.price,
            unit=latest_price.unit,
            date=latest_price.date,
            tag=tag_result.tag,
            base_price=tag_result.base_price,
            ratio=tag_result.ratio,
            origin=latest_price.origin,
            source=latest_price.source
        )
