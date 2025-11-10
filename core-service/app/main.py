from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.items.router import router as items_router
from app.aliases.router import router as aliases_router
from app.prices.router import router as prices_router
from app.exceptions import AppException
from app.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

app = FastAPI(
    title="Seafood Price Tracker Core Service",
    description="도메인 로직 및 가격 태깅 서비스",
    version="1.0.0"
)

# 예외 핸들러 등록
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(items_router)
app.include_router(aliases_router)
app.include_router(prices_router)

@app.get("/")
async def root():
    return {"message": "Core Service is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
