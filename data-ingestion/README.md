# Data Ingestion Service

수산물 가격 정보를 외부 소스에서 자동으로 수집하는 배치 서비스입니다.

## 기능

- **자동 스케줄링**: APScheduler를 사용하여 정해진 시간에 데이터 수집 (기본: 08:30, 11:30, 15:30)
- **어댑터 패턴**: 각 시장별 독립적인 어댑터로 확장 가능
- **데이터 정규화**: 품목명 매핑 및 단위 표준화
- **에러 처리**: 개별 어댑터 실패 시에도 다른 어댑터 계속 실행

## 지원 시장

### 1. 가락시장 (GarakAdapter)
- **데이터 소스**: 공공데이터 포털 API
- **수집 항목**: 품목명, 가격, 단위, 산지
- **필요 설정**: `GARAK_API_KEY` 환경변수

### 2. 노량진수산시장 (NoryangjinAdapter)
- **데이터 소스**: 웹 스크래핑
- **수집 항목**: 품목명, 가격, 단위, 산지
- **필요 설정**: `NORYANGJIN_URL` 환경변수 (선택사항)

## 설치 및 실행

### 로컬 환경

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 API 키 등 설정

# 스케줄러 실행
python scheduler.py
```

### Docker 환경

```bash
# 이미지 빌드
docker build -t seafood/data-ingestion .

# 컨테이너 실행
docker run -d \
  --name data-ingestion \
  --env-file .env \
  seafood/data-ingestion
```

### Docker Compose

```bash
# docker-compose.yml에 정의된 대로 실행
docker-compose up -d ingestion
```

## 환경변수

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `DATABASE_URL` | PostgreSQL 연결 URL | - | ✓ |
| `SCHEDULE_TIMES` | 스케줄 시간 (쉼표 구분) | `08:30,11:30,15:30` | |
| `GARAK_API_KEY` | 가락시장 API 키 | - | ✓ |
| `NORYANGJIN_URL` | 노량진 웹사이트 URL | 기본 URL | |
| `RUN_IMMEDIATELY` | 시작 시 즉시 실행 여부 | `false` | |

## 아키텍처

```
┌─────────────────────────────────────────┐
│      DataIngestionScheduler             │
│  (APScheduler로 정기 실행)               │
└──────────────┬──────────────────────────┘
               │
               ├──► GarakAdapter
               │    └─► 공공데이터 API 호출
               │
               ├──► NoryangjinAdapter
               │    └─► 웹 스크래핑
               │
               ▼
        DataNormalizer
        (품목명 매핑 + 단위 변환)
               │
               ▼
        PriceRepository
        (DB 저장)
```

## 새로운 시장 추가하기

1. `adapters/` 디렉토리에 새 어댑터 파일 생성
2. `MarketAdapter` 추상 클래스 상속
3. `fetch_data()` 및 `get_market_id()` 메서드 구현
4. `scheduler.py`의 `initialize_components()`에 어댑터 추가

예시:

```python
# adapters/new_market.py
from .base import MarketAdapter, RawPriceData

class NewMarketAdapter(MarketAdapter):
    MARKET_ID = 3
    
    def get_market_id(self) -> int:
        return self.MARKET_ID
    
    def fetch_data(self, date: datetime) -> List[RawPriceData]:
        # 데이터 수집 로직 구현
        pass
```

## 로그

- **콘솔 출력**: 실시간 로그
- **파일 출력**: `data_ingestion.log`

로그 레벨은 환경변수 `LOG_LEVEL`로 조정 가능 (기본: INFO)

## 트러블슈팅

### 데이터가 수집되지 않음

1. API 키가 올바른지 확인
2. 네트워크 연결 확인
3. 로그 파일에서 에러 메시지 확인

### 품목명 매칭 실패

- `item_aliases` 테이블에 별칭 추가 필요
- Core Service의 AliasMatcher 로그 확인

### 스케줄러가 실행되지 않음

- 환경변수 `SCHEDULE_TIMES` 형식 확인 (HH:MM,HH:MM)
- 시간대(timezone) 설정 확인

## 개발

### 테스트

```bash
# 즉시 실행 테스트
RUN_IMMEDIATELY=true python scheduler.py
```

### 디버깅

```bash
# 로그 레벨 변경
LOG_LEVEL=DEBUG python scheduler.py
```
