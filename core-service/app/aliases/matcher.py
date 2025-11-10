"""품목 별칭 매칭 모듈"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
import Levenshtein

from app.database.models import ItemAlias, Item


logger = logging.getLogger(__name__)


class AliasMatcher:
    """
    품목 별칭 매칭 클래스
    
    원본 품목명(시장에서 수집한 이름)을 표준 Item ID로 매핑합니다.
    1. 정확한 매칭 시도
    2. 유사도 기반 매칭 (Levenshtein distance)
    3. 매칭 실패 시 로그 기록
    """
    
    def __init__(self, db: Session, similarity_threshold: float = 0.85):
        """
        Args:
            db: 데이터베이스 세션
            similarity_threshold: 유사도 임계값 (0.0 ~ 1.0)
        """
        self.db = db
        self.similarity_threshold = similarity_threshold
    
    def match_item(self, raw_name: str, market_id: int) -> Optional[int]:
        """
        원본 품목명을 표준 Item ID로 매핑
        
        Args:
            raw_name: 원본 품목명 (시장에서 수집한 이름)
            market_id: 시장 ID
            
        Returns:
            매칭된 Item ID 또는 None
        """
        # 1. 정확한 매칭 시도
        exact_match = self._find_exact_match(raw_name, market_id)
        if exact_match:
            logger.debug(
                f"Exact match found: '{raw_name}' -> Item ID {exact_match}"
            )
            return exact_match
        
        # 2. 유사도 기반 매칭
        similar_match = self._find_similar_match(raw_name, market_id)
        if similar_match:
            logger.info(
                f"Similar match found: '{raw_name}' -> Item ID {similar_match}"
            )
            return similar_match
        
        # 3. 매칭 실패
        logger.warning(
            f"Unmatched item: '{raw_name}' from market {market_id}"
        )
        return None
    
    def _find_exact_match(self, raw_name: str, market_id: int) -> Optional[int]:
        """
        정확한 매칭 찾기
        
        Args:
            raw_name: 원본 품목명
            market_id: 시장 ID
            
        Returns:
            매칭된 Item ID 또는 None
        """
        alias = self.db.query(ItemAlias).filter(
            ItemAlias.raw_name == raw_name,
            ItemAlias.market_id == market_id
        ).first()
        
        return alias.item_id if alias else None
    
    def _find_similar_match(self, raw_name: str, market_id: int) -> Optional[int]:
        """
        유사도 기반 매칭 찾기 (Levenshtein distance 사용)
        
        Args:
            raw_name: 원본 품목명
            market_id: 시장 ID
            
        Returns:
            매칭된 Item ID 또는 None
        """
        # 해당 시장의 모든 별칭 조회
        aliases = self.db.query(ItemAlias).filter(
            ItemAlias.market_id == market_id
        ).all()
        
        best_match = None
        best_similarity = 0.0
        
        for alias in aliases:
            similarity = self._calculate_similarity(raw_name, alias.raw_name)
            
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = alias.item_id
        
        if best_match:
            logger.debug(
                f"Best similarity: {best_similarity:.2f} for '{raw_name}'"
            )
        
        return best_match
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        두 문자열 간의 유사도 계산 (0.0 ~ 1.0)
        
        Levenshtein distance를 사용하여 정규화된 유사도를 계산합니다.
        
        Args:
            str1: 첫 번째 문자열
            str2: 두 번째 문자열
            
        Returns:
            유사도 (0.0 ~ 1.0)
        """
        if not str1 or not str2:
            return 0.0
        
        # Levenshtein distance 계산
        distance = Levenshtein.distance(str1, str2)
        
        # 정규화 (0.0 ~ 1.0)
        max_len = max(len(str1), len(str2))
        similarity = 1.0 - (distance / max_len)
        
        return similarity
    
    def add_alias(
        self, 
        item_id: int, 
        market_id: int, 
        raw_name: str, 
        confidence: float = 1.0
    ) -> bool:
        """
        새로운 별칭 추가
        
        Args:
            item_id: 품목 ID
            market_id: 시장 ID
            raw_name: 원본 품목명
            confidence: 매칭 신뢰도 (0.0 ~ 1.0)
            
        Returns:
            성공 여부
        """
        try:
            # 중복 확인
            existing = self.db.query(ItemAlias).filter(
                ItemAlias.market_id == market_id,
                ItemAlias.raw_name == raw_name
            ).first()
            
            if existing:
                logger.warning(
                    f"Alias already exists: '{raw_name}' for market {market_id}"
                )
                return False
            
            # 새 별칭 추가
            new_alias = ItemAlias(
                item_id=item_id,
                market_id=market_id,
                raw_name=raw_name,
                confidence=confidence
            )
            self.db.add(new_alias)
            self.db.commit()
            
            logger.info(
                f"Added new alias: '{raw_name}' -> Item ID {item_id} "
                f"(market {market_id}, confidence {confidence:.2f})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alias: {e}")
            self.db.rollback()
            return False
    
    def get_unmatched_items(self, limit: int = 100) -> list[dict]:
        """
        매칭되지 않은 품목 로그 조회 (관리자용)
        
        실제 구현에서는 별도의 unmatched_items 테이블이나 로그 파일을 사용할 수 있습니다.
        여기서는 간단히 구조만 제공합니다.
        
        Args:
            limit: 최대 결과 수
            
        Returns:
            매칭되지 않은 품목 리스트
        """
        # TODO: 실제 구현 시 unmatched_items 테이블 또는 로그 파일에서 조회
        return []
