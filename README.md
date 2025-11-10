# 수산물 가격 추적 시스템 (Seafood Price Tracker)

수산물 가격 정보를 추적하고 분석하는 모바일 애플리케이션 시스템입니다.

## 시스템 구성

### 서비스 구조
- **BFF (Backend For Frontend)**: NestJS 기반 API Gateway
- **Core Service**: FastAPI 기반 도메인 로직 서비스
- **ML Service**: FastAPI 기반 이미지 인식 서비스
- **Data Ingestion**: Python 기반 데이터 수집 서비스
- **Mobile App**: Flutter 기반 모바일 애플리케이션

### 인프라
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 캐싱 레이어
- **Docker**: 컨테이너화 및 배포

## 빠른 시작

### 사전 요구사항
- Docker & Docker Compose
- Node.js 20+ (BFF 개발용)
- Python 3.11+ (백엔드 개발용)
- Flutter 3.x (모바일 개발용)

### 전체 시스템 실행

```bash
# 환경 변수 설정
cp .env.example .env

# Docker Compose로 모든 서비스 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 서비스 접근
- BFF API: http://localhost:3000
- BFF Swagger: http://localhost:3000/api/docs
- Core Service: http://localhost:8000
- ML Service: http://localhost:8001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 개발 가이드

### BFF 개발
```bash
cd bff
npm install
npm run start:dev
```

### Core Service 개발
```bash
cd core-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### ML Service 개발
```bash
cd ml-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Mobile App 개발
```bash
cd mobile
flutter pub get
flutter run
```

## 데이터베이스

### 스키마 초기화
데이터베이스 스키마는 Docker Compose 실행 시 자동으로 초기화됩니다.

수동 초기화:
```bash
psql -h localhost -U user -d seafood -f database/init.sql
psql -h localhost -U user -d seafood -f database/seed_data.sql
```

### 주요 테이블
- `items`: 품목 정보
- `markets`: 시장 정보
- `market_prices`: 시장별 가격 데이터
- `price_rules`: 가격 태깅 규칙
- `item_aliases`: 품목 별칭 매핑

## 아키텍처

```
┌─────────────────┐
│   Mobile App    │ (Flutter)
└────────┬────────┘
         │ HTTPS/REST
         ▼
┌─────────────────┐      ┌──────────────┐
│   BFF/Gateway   │◄────►│    Redis     │
└────────┬────────┘      └──────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Core Service │ │  ML Service  │ │  PostgreSQL  │
└──────────────┘ └──────────────┘ └──────────────┘
                                          ▲
                                          │
                                  ┌──────────────┐
                                  │   Data       │
                                  │  Ingestion   │
                                  └──────────────┘
```

## 주요 기능

1. **이미지 인식**: 수산물 사진으로 품목 자동 인식
2. **가격 조회**: 주요 시장의 실시간 가격 정보
3. **가격 태깅**: 평소 대비 가격 상태 분석 (높음/보통/낮음)
4. **가격 추이**: 7일/30일/90일 가격 변동 차트
5. **제철 정보**: 품목별 제철 기간 표시
6. **자동 수집**: 시장 데이터 자동 수집 (하루 3회)

## 라이선스

MIT License
