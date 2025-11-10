"""
데이터 정규화 모듈

원본 시장 데이터를 표준 형식으로 변환합니다.
- 품목명 매핑 (AliasMatcher 활용)
- 단위 변환 (kg, 마리, 상자 표준화)
- 가격 검증 및 정제
"""
from typing import List, Optional
import logging
from adapters.base import RawPriceData

logger = logging.getLogger(__name__)


class DataNormalizer:
    """데이터 정규화 클래스"""
    
    def __init__(self, alias_matcher):
        """
        Args:
            alias_matcher: AliasMatcher 인스턴스 (품목명 매핑용)
        """
        self.alias_matcher = alias_matcher
        self.stats = {
            'total': 0,
            'matched': 0,
            'unmatched': 0,
            'invalid': 0
        }
    
    def normalize(self, raw_data: List[RawPriceData], market_id: int) -> List[dict]:
        """
        원본 데이터를 정규화
        
        1. 품목명 매핑 (AliasMatcher 활용)
        2. 단위 변환 (kg, 마리, 상자 표준화)
        3. 가격 검증
        
        Args:
            raw_data: 원본 가격 데이터 리스트
            market_id: 시장 ID
            
        Returns:
            정규화된 데이터 딕셔너리 리스트
        """
        normalized = []
        self.stats = {'total': 0, 'matched': 0, 'unmatched': 0, 'invalid': 0}
        
        for data in raw_data:
            self.stats['total'] += 1
            
            # 데이터 검증
            if not self._validate_data(data):
                self.stats['invalid'] += 1
                continue
            
            # 품목명 매핑
            item_id = self.alias_matcher.match_item(data.raw_name, market_id)
            
            if item_id is None:
                # 매핑 실패 시 스킵
                self.stats['unmatched'] += 1
                logger.debug(
                    f"Unmatched item: '{data.raw_name}' "
                    f"(market_id={market_id}, price={data.price})"
                )
                continue
            
            self.stats['matched'] += 1
            
            normalized.append({
                'item_id': item_id,
                'market_id': market_id,
                'date': data.date,
                'price': data.price,
                'unit': self._normalize_unit(data.unit),
                'origin': data.origin or '',
                'source': data.source or '',
            })
        
        # 통계 로깅
        logger.info(
            f"Normalization complete: "
            f"total={self.stats['total']}, "
            f"matched={self.stats['matched']}, "
            f"unmatched={self.stats['unmatched']}, "
            f"invalid={self.stats['invalid']}"
        )
        
        return normalized
    
    def _validate_data(self, data: RawPriceData) -> bool:
        """
        데이터 유효성 검증
        
        Args:
            data: 원본 가격 데이터
            
        Returns:
            유효 여부
        """
        # 품목명 검증
        if not data.raw_name or not data.raw_name.strip():
            logger.warning("Empty item name")
            return False
        
        # 가격 검증
        if data.price <= 0:
            logger.warning(
                f"Invalid price for '{data.raw_name}': {data.price}"
            )
            return False
        
        # 가격 범위 검증 (너무 높거나 낮은 가격 필터링)
        if data.price > 1000000:  # 100만원 초과
            logger.warning(
                f"Price too high for '{data.raw_name}': {data.price}"
            )
            return False
        
        # 단위 검증
        if not data.unit or not data.unit.strip():
            logger.warning(f"Empty unit for '{data.raw_name}'")
            return False
        
        return True
    
    def _normalize_unit(self, unit: str) -> str:
        """
        단위 표준화
        
        Args:
            unit: 원본 단위
            
        Returns:
            표준화된 단위
        """
        if not unit:
            return 'kg'
        
        unit_lower = unit.lower().strip()
        
        # 단위 매핑 테이블
        unit_map = {
            'kg': 'kg',
            'kilogram': 'kg',
            '킬로그램': 'kg',
            '킬로': 'kg',
            'kilo': 'kg',
            '마리': '마리',
            'ea': '마리',
            'each': '마리',
            'pcs': '마리',
            '개': '마리',
            '상자': '상자',
            'box': '상자',
            '박스': '상자',
        }
        
        # 매핑 테이블에서 찾기
        normalized = unit_map.get(unit_lower)
        
        if normalized:
            return normalized
        
        # 매핑되지 않은 단위는 로그 기록 후 원본 반환
        logger.debug(f"Unknown unit: '{unit}', using as-is")
        return unit
    
    def get_stats(self) -> dict:
        """
        정규화 통계 반환
        
        Returns:
            통계 딕셔너리
        """
        return self.stats.copy()
