"""
API 재시도 전략

API 호출 실패 시 재시도 로직을 제공합니다.
"""
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class RetryStrategy:
    """API 재시도 전략 클래스
    
    Exponential backoff와 Rate limit 처리를 포함한 재시도 로직을 제공합니다.
    """
    
    @staticmethod
    def should_retry(error: Exception, attempt: int) -> bool:
        """재시도 여부 판단
        
        Args:
            error: 발생한 예외
            attempt: 현재 시도 횟수 (1부터 시작)
            
        Returns:
            bool: 재시도 여부
        """
        # 최대 재시도 횟수 초과
        if attempt >= 3:
            logger.debug(f"최대 재시도 횟수 초과: {attempt}회")
            return False
        
        # Timeout 에러는 재시도
        if isinstance(error, (requests.Timeout, TimeoutError)):
            logger.debug("Timeout 에러 - 재시도")
            return True
        
        # Connection 에러는 재시도
        if isinstance(error, requests.ConnectionError):
            logger.debug("Connection 에러 - 재시도")
            return True
        
        # HTTP 에러 처리
        if isinstance(error, requests.HTTPError):
            status_code = error.response.status_code
            
            # 5xx 서버 에러는 재시도
            if 500 <= status_code < 600:
                logger.debug(f"서버 에러 {status_code} - 재시도")
                return True
            
            # 429 Rate Limit은 재시도
            if status_code == 429:
                logger.debug("Rate Limit 에러 - 재시도")
                return True
            
            # 408 Request Timeout은 재시도
            if status_code == 408:
                logger.debug("Request Timeout - 재시도")
                return True
            
            # 4xx 클라이언트 에러는 재시도 안함
            if 400 <= status_code < 500:
                logger.debug(f"클라이언트 에러 {status_code} - 재시도 안함")
                return False
        
        # 기타 에러는 재시도 안함
        logger.debug(f"기타 에러 {type(error).__name__} - 재시도 안함")
        return False
    
    @staticmethod
    def get_delay(attempt: int, error: Exception) -> int:
        """재시도 대기 시간 계산
        
        Exponential backoff 전략을 사용합니다:
        - 1차 시도 실패: 1초 대기
        - 2차 시도 실패: 2초 대기
        - 3차 시도 실패: 4초 대기
        
        Rate Limit의 경우 Retry-After 헤더를 우선 사용합니다.
        
        Args:
            attempt: 현재 시도 횟수 (1부터 시작)
            error: 발생한 예외
            
        Returns:
            int: 대기 시간 (초)
        """
        # Rate Limit의 경우 Retry-After 헤더 확인
        if isinstance(error, requests.HTTPError):
            if error.response.status_code == 429:
                retry_after = RetryStrategy._get_retry_after(error)
                if retry_after:
                    logger.debug(f"Retry-After 헤더 사용: {retry_after}초")
                    return retry_after
        
        # Exponential backoff: 2^(attempt-1) 초
        # attempt=1 -> 1초, attempt=2 -> 2초, attempt=3 -> 4초
        delay = 2 ** (attempt - 1)
        logger.debug(f"Exponential backoff: {delay}초 (시도 {attempt}회)")
        return delay
    
    @staticmethod
    def _get_retry_after(error: requests.HTTPError) -> Optional[int]:
        """Retry-After 헤더 값 추출
        
        Args:
            error: HTTP 에러
            
        Returns:
            Optional[int]: Retry-After 값 (초), 없으면 None
        """
        try:
            retry_after = error.response.headers.get('Retry-After')
            if retry_after:
                # 숫자 형식 (초)
                if retry_after.isdigit():
                    return int(retry_after)
                
                # HTTP-date 형식은 지원하지 않음 (복잡도 증가)
                logger.warning(f"Retry-After HTTP-date 형식은 지원하지 않음: {retry_after}")
                return None
        except Exception as e:
            logger.warning(f"Retry-After 헤더 파싱 실패: {e}")
            return None
        
        return None
    
    @staticmethod
    def log_retry_attempt(
        adapter_name: str,
        attempt: int,
        max_retries: int,
        error: Exception,
        delay: int
    ):
        """재시도 로그 기록
        
        Args:
            adapter_name: 어댑터 이름
            attempt: 현재 시도 횟수
            max_retries: 최대 재시도 횟수
            error: 발생한 예외
            delay: 대기 시간 (초)
        """
        logger.warning(
            f"{adapter_name} 재시도 {attempt}/{max_retries}",
            extra={
                'adapter': adapter_name,
                'attempt': attempt,
                'max_retries': max_retries,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'delay': delay
            }
        )
    
    @staticmethod
    def log_final_failure(
        adapter_name: str,
        max_retries: int,
        error: Exception
    ):
        """최종 실패 로그 기록
        
        Args:
            adapter_name: 어댑터 이름
            max_retries: 최대 재시도 횟수
            error: 발생한 예외
        """
        logger.error(
            f"{adapter_name} 최종 실패 (재시도 {max_retries}회)",
            extra={
                'adapter': adapter_name,
                'max_retries': max_retries,
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
        )
