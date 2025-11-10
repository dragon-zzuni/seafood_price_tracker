"""
커스텀 예외 클래스 정의
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for all application errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ItemNotFoundException(AppException):
    """품목을 찾을 수 없음"""
    
    def __init__(self, item_id: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"품목을 찾을 수 없습니다 (ID: {item_id})",
            status_code=404,
            details=details or {"item_id": item_id}
        )


class PriceDataNotFoundException(AppException):
    """가격 데이터를 찾을 수 없음"""
    
    def __init__(
        self,
        item_id: int,
        market_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"가격 데이터가 없습니다 (품목 ID: {item_id}"
        if market_id:
            message += f", 시장 ID: {market_id}"
        message += ")"
        
        super().__init__(
            message=message,
            status_code=404,
            details=details or {"item_id": item_id, "market_id": market_id}
        )


class MarketNotFoundException(AppException):
    """시장을 찾을 수 없음"""
    
    def __init__(self, market_id: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"시장을 찾을 수 없습니다 (ID: {market_id})",
            status_code=404,
            details=details or {"market_id": market_id}
        )


class AliasNotFoundException(AppException):
    """별칭을 찾을 수 없음"""
    
    def __init__(self, raw_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"품목 별칭을 찾을 수 없습니다: {raw_name}",
            status_code=404,
            details=details or {"raw_name": raw_name}
        )


class InvalidDateRangeException(AppException):
    """잘못된 날짜 범위"""
    
    def __init__(self, message: str = "잘못된 날짜 범위입니다", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details
        )


class DatabaseException(AppException):
    """데이터베이스 오류"""
    
    def __init__(self, message: str = "데이터베이스 오류가 발생했습니다", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )


class ValidationException(AppException):
    """입력 검증 오류"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details
        )
