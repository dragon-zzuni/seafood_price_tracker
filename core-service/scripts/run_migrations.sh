#!/bin/bash
# Alembic 마이그레이션 실행 스크립트

echo "Running database migrations..."

# 현재 마이그레이션 상태 확인
alembic current

# 최신 버전으로 마이그레이션
alembic upgrade head

echo "Migrations completed!"
