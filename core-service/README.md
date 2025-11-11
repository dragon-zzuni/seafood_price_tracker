# Core Service

수산물 가격 추적 시스템의 핵심 도메인 서비스입니다.

## 기능

- 품목 관리 및 검색
- 시장 가격 조회 및 분석
- 가격 태깅 (높음/보통/낮음)
- 품목 별칭 매핑

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **SQLAlchemy**: ORM
- **PostgreSQL**: 데이터베이스
- **Alembic**: 마이그레이션 도구
- **Redis**: 캐싱

## 프로젝트 구조

```
core-service/
├── app/
│   ├── database/           # 데이터베이스 레이어
│   │   ├── models.py       # SQLAlchemy 모델
│   │   ├── connection.py   # DB 연결 설정
│   │   ├── base_repository.py  # 베이스 리포지토리
│   │   ├── item_repository.py  # 품목 리포지토리
│   │   ├── market_repository.py  # 시장 리포지토리
│   │   ├── price_repository.py  # 가격 리포지토리
│   │   ├── price_rule_repository.py  # 가격 규칙 리포지토리
│   │   └── alias_repository.py  # 별칭 리포지토리
│   ├── items/              # 품목 관리 모듈
│   ├── prices/             # 가격 조회 모듈
│   ├── tagging/            # 가격 태깅 모듈
│   ├── aliases/            # 별칭 매핑 모듈
│   └── main.py             # FastAPI 앱
├── alembic/                # 마이그레이션
│   └── versions/
│       ├── 001_initial_schema.py  # 초기 스키마
│       └── 002_seed_data.py       # 시드 데이터
├── scripts/                # 유틸리티 스크립트
│   ├── init_db.py          # DB 초기화
│   ├── run_migrations.sh   # 마이그레이션 실행 (Linux/Mac)
│   └── run_migrations.bat  # 마이그레이션 실행 (Windows)
├── tests/                  # 테스트
│   └── test_repositories.py
├── requirements.txt
└── Dockerfile

```

## 설치 및 실행

### 1. 환경 변수 설정

- Docker Compose 사용 시 루트 디렉터리의 `.env` 파일을 통해 `DATABASE_URL`, `REDIS_URL`이 자동으로 주입됩니다.
- 독립 실행 시에는 아래 환경 변수를 직접 지정하세요:
  ```bash
  export DATABASE_URL=postgresql://user:pass@localhost:5432/seafood
  export REDIS_URL=redis://localhost:6379
  ```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션

#### Linux/Mac:
```bash
chmod +x scripts/run_migrations.sh
./scripts/run_migrations.sh
```

#### Windows:
```cmd
scripts\run_migrations.bat
```

#### 또는 직접 Alembic 명령 사용:
```bash
# 현재 마이그레이션 상태 확인
alembic current

# 최신 버전으로 마이그레이션
alembic upgrade head

# 특정 버전으로 마이그레이션
alembic upgrade 001

# 마이그레이션 롤백
alembic downgrade -1
```

### 4. 서비스 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 데이터베이스 스키마

### Items (품목)
- 품목 정보 (한글명, 영문명, 카테고리)
- 제철 기간 (season_start, season_end)
- 기본 산지 및 단위

### Markets (시장)
- 시장 정보 (이름, 코드, 타입)

### MarketPrices (시장 가격)
- 품목별, 시장별, 날짜별 가격 데이터
- 단위, 산지, 출처 정보

### PriceRules (가격 규칙)
- 품목별 가격 태깅 임계값
- 높음/낮음 기준 (기본값: 1.15/0.90)

### ItemAliases (품목 별칭)
- 시장별 품목명 매핑
- 신뢰도 점수

## 리포지토리 사용 예시

```python
from app.database import get_db, ItemRepository, PriceRepository

# FastAPI 엔드포인트에서 사용
@app.get("/items/search")
async def search_items(query: str, db: Session = Depends(get_db)):
    repo = ItemRepository(db)
    items = repo.search_by_name(query, limit=10)
    return items

# 가격 조회
@app.get("/prices/latest")
async def get_latest_price(item_id: int, market_id: int, db: Session = Depends(get_db)):
    repo = PriceRepository(db)
    price = repo.get_latest_price(item_id, market_id)
    return price

# 평균 가격 계산
@app.get("/prices/average")
async def get_average_price(item_id: int, market_id: int, db: Session = Depends(get_db)):
    repo = PriceRepository(db)
    avg_price = repo.get_average_price(item_id, market_id, days=30)
    return {"average_price": avg_price}
```

## 테스트

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_repositories.py -v

# 커버리지 포함
pytest --cov=app tests/
```

## Docker 실행

```bash
# 이미지 빌드
docker build -t seafood-core-service .

# 컨테이너 실행
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/seafood \
  seafood-core-service
```

## API 문서

서비스 실행 후 다음 URL에서 API 문서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 개발 가이드

### 새 마이그레이션 생성

```bash
# 자동 생성 (모델 변경 감지)
alembic revision --autogenerate -m "설명"

# 수동 생성
alembic revision -m "설명"
```

### 새 리포지토리 추가

1. `app/database/` 디렉토리에 새 리포지토리 파일 생성
2. `BaseRepository`를 상속받아 구현
3. `app/database/__init__.py`에 추가

```python
from app.database.base_repository import BaseRepository
from app.database.models import YourModel

class YourRepository(BaseRepository[YourModel]):
    def __init__(self, db: Session):
        super().__init__(YourModel, db)
    
    # 커스텀 메서드 추가
    def custom_query(self, param):
        return self.db.query(YourModel).filter(...).all()
```

## 문제 해결

### 마이그레이션 오류
```bash
# 마이그레이션 히스토리 확인
alembic history

# 특정 버전으로 강제 설정
alembic stamp head
```

### 데이터베이스 연결 오류
- `.env` 파일의 `DATABASE_URL` 확인
- PostgreSQL 서비스 실행 상태 확인
- 방화벽 설정 확인

## 라이선스

MIT
