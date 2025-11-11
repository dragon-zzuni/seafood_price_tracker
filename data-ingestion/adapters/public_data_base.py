"""
공공데이터 API 어댑터 기본 클래스

공공데이터 포털의 다양한 API를 통합하기 위한 기본 어댑터 클래스를 제공합니다.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import logging
import requests
import time
import hashlib
import json

logger = logging.getLogger(__name__)


class DataCategory(Enum):
    """데이터 카테고리"""
    PRICE = "price"
    METADATA = "metadata"
    CERTIFICATION = "certification"
    REGULATION = "regulation"


class BasePublicDataAdapter(ABC):
    """공공데이터 API 어댑터 기본 클래스
    
    공통 기능:
    - API 호출 로직 (재시도, 타임아웃)
    - 에러 처리 및 로깅
    - 캐시 키 생성
    """
    
    def __init__(self, api_key: str, base_url: str):
        """
        Args:
            api_key: 공공데이터 API 키
            base_url: API 기본 URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = 30  # 초
        self.max_retries = 3
        self.session = requests.Session()
        
    @abstractmethod
    def get_category(self) -> DataCategory:
        """데이터 카테고리 반환
        
        Returns:
            DataCategory: 어댑터가 수집하는 데이터의 카테고리
        """
        pass
    
    @abstractmethod
    def fetch_data(self, date: Optional[datetime] = None, **kwargs) -> List[Dict[str, Any]]:
        """데이터 수집
        
        Args:
            date: 수집할 데이터의 날짜 (선택적)
            **kwargs: 추가 파라미터
            
        Returns:
            List[Dict[str, Any]]: 수집된 데이터 리스트
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: Dict) -> List[Dict[str, Any]]:
        """API 응답 파싱
        
        Args:
            response: API 응답 딕셔너리
            
        Returns:
            List[Dict[str, Any]]: 파싱된 데이터 리스트
        """
        pass
    
    def get_cache_key(self, **kwargs) -> str:
        """캐시 키 생성
        
        Args:
            **kwargs: 캐시 키 생성에 사용할 파라미터
            
        Returns:
            str: 생성된 캐시 키
        """
        # 어댑터 이름과 파라미터를 조합하여 고유한 캐시 키 생성
        adapter_name = self.__class__.__name__
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        key_source = f"{adapter_name}:{params_str}"
        
        # SHA256 해시로 키 생성
        hash_obj = hashlib.sha256(key_source.encode())
        return f"public_data:{adapter_name}:{hash_obj.hexdigest()[:16]}"
    
    def get_cache_ttl(self) -> int:
        """캐시 TTL (초) 반환
        
        카테고리별 기본 TTL:
        - METADATA: 24시간
        - CERTIFICATION: 12시간
        - REGULATION: 6시간
        - PRICE: 1시간
        
        Returns:
            int: TTL (초)
        """
        category = self.get_category()
        ttl_map = {
            DataCategory.METADATA: 86400,      # 24시간
            DataCategory.CERTIFICATION: 43200,  # 12시간
            DataCategory.REGULATION: 21600,     # 6시간
            DataCategory.PRICE: 3600,           # 1시간
        }
        return ttl_map.get(category, 3600)
    
    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """API 요청 실행 (재시도 로직 포함)
        
        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터
            method: HTTP 메서드
            
        Returns:
            Dict[str, Any]: API 응답
            
        Raises:
            requests.RequestException: API 요청 실패 시
        """
        from .retry_strategy import RetryStrategy
        
        url = f"{self.base_url}{endpoint}"
        
        # API 키를 파라미터에 추가
        if params is None:
            params = {}
        params['serviceKey'] = self.api_key
        
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                logger.info(
                    f"API 요청 시도 {attempt + 1}/{self.max_retries}: {url}",
                    extra={'params': self._sanitize_params(params)}
                )
                
                if method.upper() == "GET":
                    response = self.session.get(
                        url,
                        params=params,
                        timeout=self.timeout
                    )
                else:
                    response = self.session.post(
                        url,
                        data=params,
                        timeout=self.timeout
                    )
                
                response.raise_for_status()
                
                logger.info(f"API 요청 성공: {url}")
                return response.json()
                
            except Exception as error:
                last_error = error
                attempt += 1
                
                # 재시도 여부 판단
                if not RetryStrategy.should_retry(error, attempt):
                    logger.error(
                        f"API 요청 실패 (재시도 안함): {url}",
                        extra={'error': str(error)}
                    )
                    raise
                
                # 재시도 대기
                delay = RetryStrategy.get_delay(attempt, error)
                logger.warning(
                    f"API 요청 실패, {delay}초 후 재시도: {url}",
                    extra={'error': str(error), 'attempt': attempt}
                )
                time.sleep(delay)
        
        # 모든 재시도 실패
        logger.error(
            f"API 요청 최종 실패: {url}",
            extra={'error': str(last_error), 'attempts': self.max_retries}
        )
        raise last_error
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """로그용 파라미터 정제 (API 키 마스킹)
        
        Args:
            params: 원본 파라미터
            
        Returns:
            Dict[str, Any]: 정제된 파라미터
        """
        sanitized = params.copy()
        if 'serviceKey' in sanitized:
            key = sanitized['serviceKey']
            if len(key) > 8:
                sanitized['serviceKey'] = f"{key[:4]}...{key[-4:]}"
        return sanitized
    
    def log_collection_stats(
        self,
        success_count: int,
        failure_count: int,
        duplicate_count: int,
        execution_time: float
    ):
        """데이터 수집 통계 로깅
        
        Args:
            success_count: 성공 건수
            failure_count: 실패 건수
            duplicate_count: 중복 건수
            execution_time: 실행 시간 (초)
        """
        logger.info(
            f"{self.__class__.__name__} 수집 완료",
            extra={
                'adapter': self.__class__.__name__,
                'category': self.get_category().value,
                'success': success_count,
                'failure': failure_count,
                'duplicate': duplicate_count,
                'execution_time': f"{execution_time:.2f}s"
            }
        )
