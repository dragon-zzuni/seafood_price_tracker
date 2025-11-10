@echo off
REM Alembic 마이그레이션 실행 스크립트 (Windows)

echo Running database migrations...

REM 현재 마이그레이션 상태 확인
alembic current

REM 최신 버전으로 마이그레이션
alembic upgrade head

echo Migrations completed!
pause
