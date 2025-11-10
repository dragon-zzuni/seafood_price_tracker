"""
FastAPI 예외 핸들러
"""
import logging
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import AppException

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_type: str,
    details: dict = None
) -> JSONResponse:
    """표준 JSON 에러 응답 생성"""
    content = {
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """커스텀 애플리케이션 예외 핸들러"""
    logger.warning(
        f"Application exception: {exc.__class__.__name__}",
        extra={
            "path": request.url.path,
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_type=exc.__class__.__name__,
        details=exc.details
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """FastAPI 입력 검증 예외 핸들러"""
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors()
        }
    )
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="입력 데이터가 올바르지 않습니다",
        error_type="ValidationError",
        details={"validation_errors": exc.errors()}
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """SQLAlchemy 데이터베이스 예외 핸들러"""
    logger.error(
        "Database error",
        extra={
            "path": request.url.path,
            "error": str(exc)
        },
        exc_info=True
    )
    
    # 5xx 오류는 상세 정보 숨김 (보안)
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="데이터베이스 오류가 발생했습니다",
        error_type="DatabaseError"
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """일반 예외 핸들러"""
    logger.error(
        "Unexpected error",
        extra={
            "path": request.url.path,
            "error": str(exc)
        },
        exc_info=True
    )
    
    # 5xx 오류는 상세 정보 숨김 (보안)
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요",
        error_type="InternalServerError"
    )
