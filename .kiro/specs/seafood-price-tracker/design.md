# Design Document

## Overview

수산물 가격 정보 추적 시스템은 마이크로서비스 아키텍처를 기반으로 하며, 모바일 앱, BFF, Core Service, ML Service, Data Ingestion Service로 구성됩니다. 각 서비스는 독립적으로 배포 가능하며, 명확한 책임 분리를 통해 유지보수성과 확장성을 확보합니다.

**핵심 설계 원칙:**
- 모듈화: 각 기능을 독립적인 모듈로 분리
- 확장성: 새로운 시장/품목 추가 시 기존 코드 수정 최소화
- 성능: 캐싱 전략으로 500ms 이내 응답 보장
- 유연성: ML 모델 교체 가능한 인터페이스 설계

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Mobile App    │ (Flutter)
│   (iOS/Android) │
└────────┬────────┘
         │ HTTPS/REST
         ▼
┌─────────────────┐      ┌──────────────┐
│   BFF/Gateway   │◄────►│    Redis     │
│   (NestJS)      │      │   (Cache)    │
└────────┬────────┘      └──────────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Core Service │ │  ML Service  │ │   Data       │ │  PostgreSQL  │
│  (FastAPI)   │ │  (FastAPI)   │ │  Ingestion   │ │   Database   │
│              │ │              │ │  (Python)    │ │              │
└──────────────┘ └──────────────┘ └──────┬───────┘ └──────────────┘
                                          │
                                          ▼
                                  ┌──────────────┐
                                  │ External APIs│
                                  │ (공공데이터)  │
                                  └──────────────┘
```


### Service Responsibilities

#### 1. Mobile App (Flutter)
- **책임**: 사용자 인터페이스, 로컬 상태 관리, 이미지 캡처
- **기술**: Flutter 3.x, Riverpod, dio, fl_chart
- **모듈 구조**:
  - `lib/presentation/`: UI 위젯 및 화면
  - `lib/application/`: 상태 관리 (Riverpod providers)
  - `lib/domain/`: 도메인 모델 및 인터페이스
  - `lib/infrastructure/`: API 클라이언트, 로컬 저장소

#### 2. BFF (Backend For Frontend)
- **책임**: API Gateway, 인증, 캐싱, 응답 포맷 변환
- **기술**: Node.js + NestJS, Redis
- **모듈 구조**:
  - `src/items/`: 품목 관련 엔드포인트
  - `src/prices/`: 가격 조회 엔드포인트
  - `src/recognition/`: 이미지 인식 프록시
  - `src/cache/`: Redis 캐시 관리
  - `src/auth/`: 인증/인가 (향후 확장)

#### 3. Core Service
- **책임**: 도메인 로직, 가격 태깅, 품목 관리
- **기술**: Python + FastAPI, SQLAlchemy
- **모듈 구조**:
  - `app/items/`: 품목 관리 모듈
  - `app/prices/`: 가격 조회 및 통계
  - `app/tagging/`: 가격 태깅 로직
  - `app/aliases/`: 품목 별칭 매핑
  - `app/database/`: DB 모델 및 리포지토리

#### 4. ML Service
- **책임**: 이미지 인식 (Detection + Classification)
- **기술**: Python + FastAPI, PyTorch, YOLO
- **모듈 구조**:
  - `app/detection/`: 객체 탐지 모듈
  - `app/classification/`: 품목 분류 모듈
  - `app/models/`: 모델 로더 및 추론 인터페이스
  - `app/preprocessing/`: 이미지 전처리

#### 5. Data Ingestion Service
- **책임**: 외부 데이터 수집, 정규화, 저장
- **기술**: Python + APScheduler
- **모듈 구조**:
  - `adapters/garak.py`: 가락시장 어댑터
  - `adapters/noryangjin.py`: 노량진 어댑터
  - `adapters/public_api.py`: 공공데이터 어댑터
  - `normalizer.py`: 데이터 정규화
  - `scheduler.py`: 배치 스케줄러


## Components and Interfaces

### 1. Mobile App Components

#### 1.1 UI Layer
```dart
// 화면 구조
screens/
  ├── home_screen.dart              // 검색 + 인기 품목
  ├── recognition_result_screen.dart // 인식 결과 선택
  ├── item_dashboard_screen.dart     // 품목 상세 대시보드
  └── settings_screen.dart           // 사용자 설정

widgets/
  ├── item_search_bar.dart          // 자동완성 검색
  ├── price_card.dart               // 시장별 가격 카드
  ├── price_chart.dart              // 가격 추이 차트
  ├── price_tag_badge.dart          // 높음/보통/낮음 배지
  └── season_indicator.dart         // 제철 표시
```

#### 1.2 State Management (Riverpod)
```dart
providers/
  ├── item_provider.dart            // 품목 검색 상태
  ├── recognition_provider.dart     // 이미지 인식 상태
  ├── dashboard_provider.dart       // 대시보드 데이터
  └── settings_provider.dart        // 사용자 설정
```

#### 1.3 API Client
```dart
// API 인터페이스
class ApiClient {
  Future<List<Item>> searchItems(String query);
  Future<RecognitionResult> recognizeImage(File image);
  Future<ItemDashboard> getItemDashboard(int itemId, DateTime date);
}
```

### 2. BFF API Endpoints

```typescript
// 품목 관련
GET  /api/items?query={query}              // 품목 검색
GET  /api/items/{id}                       // 품목 기본 정보
GET  /api/items/{id}/dashboard?date={date} // 대시보드 데이터

// 이미지 인식
POST /api/recognition                      // 이미지 업로드 및 인식

// 시장 정보
GET  /api/markets                          // 시장 리스트
```

#### 2.1 Response Format Examples

**품목 검색 응답:**
```json
{
  "items": [
    {
      "id": 11,
      "name_ko": "광어",
      "name_en": "Flounder",
      "category": "fish"
    }
  ]
}
```

**대시보드 응답:**
```json
{
  "item": {
    "id": 11,
    "name_ko": "광어",
    "season": {"from": 11, "to": 2},
    "default_origin": "제주"
  },
  "current_prices": [
    {
      "market": "가락시장",
      "price": 18500,
      "unit": "kg",
      "date": "2025-11-10",
      "tag": "보통"
    }
  ],
  "price_trend": {
    "period_days": 30,
    "data": [
      {"date": "2025-11-09", "market": "가락시장", "price": 18000}
    ]
  },
  "data_sources": ["가락시장", "공공데이터포털"]
}
```


### 3. Core Service Modules

#### 3.1 Price Tagging Module
```python
# app/tagging/price_evaluator.py
class PriceEvaluator:
    def __init__(self, price_repository, rule_repository):
        self.price_repo = price_repository
        self.rule_repo = rule_repository
    
    def calculate_tag(self, item_id: int, market_id: int, 
                     current_price: float, date: datetime) -> PriceTag:
        """
        가격 태그 계산 로직
        1. 최근 30일 평균 가격 조회
        2. 품목별 임계값 조회 (없으면 기본값)
        3. 비율 계산 및 태그 결정
        """
        base_price = self._get_base_price(item_id, market_id, date)
        thresholds = self._get_thresholds(item_id)
        
        ratio = current_price / base_price
        
        if ratio >= thresholds.high:
            return PriceTag.HIGH
        elif ratio < thresholds.low:
            return PriceTag.LOW
        else:
            return PriceTag.NORMAL
```

#### 3.2 Item Alias Module
```python
# app/aliases/alias_matcher.py
class AliasMatcher:
    def __init__(self, alias_repository):
        self.alias_repo = alias_repository
    
    def match_item(self, raw_name: str, market_id: int) -> Optional[int]:
        """
        원본 품목명을 표준 Item ID로 매핑
        1. 정확한 매칭 시도
        2. 유사도 기반 매칭 (Levenshtein distance)
        3. 매칭 실패 시 None 반환 및 로그 기록
        """
        # 정확한 매칭
        exact_match = self.alias_repo.find_by_raw_name(raw_name, market_id)
        if exact_match:
            return exact_match.item_id
        
        # 유사도 매칭 (임계값 0.85)
        similar_matches = self.alias_repo.find_similar(raw_name, threshold=0.85)
        if similar_matches:
            return similar_matches[0].item_id
        
        # 매칭 실패
        logger.warning(f"Unmatched item: {raw_name} from market {market_id}")
        return None
```

### 4. ML Service Architecture

#### 4.1 Model Interface (Strategy Pattern)
```python
# app/models/base.py
from abc import ABC, abstractmethod

class DetectionModel(ABC):
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[BoundingBox]:
        pass

class ClassificationModel(ABC):
    @abstractmethod
    def classify(self, image: np.ndarray) -> List[ClassificationResult]:
        pass

# app/models/yolo_detector.py
class YOLODetector(DetectionModel):
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
    
    def detect(self, image: np.ndarray) -> List[BoundingBox]:
        results = self.model(image)
        return self._parse_results(results)

# app/models/yolo_classifier.py
class YOLOClassifier(ClassificationModel):
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
    
    def classify(self, image: np.ndarray) -> List[ClassificationResult]:
        results = self.model(image)
        return self._parse_results(results)

# app/models/clip_classifier.py (향후 확장)
class CLIPClassifier(ClassificationModel):
    def __init__(self, model_name: str):
        self.model = CLIPModel.from_pretrained(model_name)
    
    def classify(self, image: np.ndarray) -> List[ClassificationResult]:
        # Zero-shot classification
        pass
```

#### 4.2 Recognition Pipeline
```python
# app/recognition/pipeline.py
class RecognitionPipeline:
    def __init__(self, detector: DetectionModel, 
                 classifier: ClassificationModel):
        self.detector = detector
        self.classifier = classifier
    
    def recognize(self, image: np.ndarray) -> List[RecognitionResult]:
        """
        1. Detection: 수산물 영역 탐지
        2. Classification: 각 영역의 품목 분류
        3. 신뢰도 기준 필터링 (threshold > 0.3)
        4. Top-4 결과 반환
        """
        boxes = self.detector.detect(image)
        
        results = []
        for box in boxes:
            cropped = self._crop_image(image, box)
            classifications = self.classifier.classify(cropped)
            results.extend(classifications)
        
        # 신뢰도 순 정렬 및 상위 4개
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:4]
```


### 5. Data Ingestion Adapters (Adapter Pattern)

```python
# adapters/base.py
from abc import ABC, abstractmethod

class MarketAdapter(ABC):
    @abstractmethod
    def fetch_data(self, date: datetime) -> List[RawPriceData]:
        """시장 데이터 수집"""
        pass
    
    @abstractmethod
    def get_market_id(self) -> int:
        """시장 ID 반환"""
        pass

# adapters/garak.py
class GarakAdapter(MarketAdapter):
    def __init__(self, api_client):
        self.client = api_client
    
    def fetch_data(self, date: datetime) -> List[RawPriceData]:
        """
        가락시장 API 호출
        - 품목코드, 단위, 경락가 수집
        """
        response = self.client.get_prices(date)
        return self._parse_response(response)
    
    def get_market_id(self) -> int:
        return 1  # GARAK

# adapters/noryangjin.py
class NoryangjinAdapter(MarketAdapter):
    def __init__(self, scraper):
        self.scraper = scraper
    
    def fetch_data(self, date: datetime) -> List[RawPriceData]:
        """
        노량진 웹사이트 스크래핑
        - 품목명, 원산지, 규격, 가격 수집
        """
        html = self.scraper.fetch_page(date)
        return self._parse_html(html)
    
    def get_market_id(self) -> int:
        return 2  # NORYANGJIN

# scheduler.py
class DataIngestionScheduler:
    def __init__(self, adapters: List[MarketAdapter], 
                 normalizer: DataNormalizer,
                 repository: PriceRepository):
        self.adapters = adapters
        self.normalizer = normalizer
        self.repo = repository
    
    def run_collection(self):
        """
        모든 어댑터에서 데이터 수집
        1. 각 어댑터에서 raw 데이터 수집
        2. 정규화 (품목명 매핑, 단위 변환)
        3. DB 저장
        4. 성공/실패 로그 기록
        """
        for adapter in self.adapters:
            try:
                raw_data = adapter.fetch_data(datetime.now())
                normalized = self.normalizer.normalize(raw_data, adapter.get_market_id())
                self.repo.bulk_insert(normalized)
                logger.info(f"Success: {adapter.__class__.__name__}, {len(normalized)} records")
            except Exception as e:
                logger.error(f"Failed: {adapter.__class__.__name__}, {str(e)}")
```

## Data Models

### Database Schema

```sql
-- 품목 테이블
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name_ko VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    category VARCHAR(50) NOT NULL,  -- fish, shellfish, crustacean, etc
    season_start INT,  -- 1-12 (월)
    season_end INT,    -- 1-12 (월)
    default_origin VARCHAR(100),
    unit_default VARCHAR(20),  -- kg, 마리, 상자
    created_at TIMESTAMP DEFAULT NOW()
);

-- 시장 테이블
CREATE TABLE markets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,  -- GARAK, NORYANGJIN
    type VARCHAR(50)  -- wholesale, retail
);

-- 시장 가격 테이블
CREATE TABLE market_prices (
    id SERIAL PRIMARY KEY,
    item_id INT REFERENCES items(id),
    market_id INT REFERENCES markets(id),
    date DATE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    origin VARCHAR(100),
    source VARCHAR(100),  -- 데이터 출처
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(item_id, market_id, date)
);

-- 가격 규칙 테이블 (품목별 임계값)
CREATE TABLE price_rules (
    id SERIAL PRIMARY KEY,
    item_id INT REFERENCES items(id) UNIQUE,
    high_threshold DECIMAL(3, 2) DEFAULT 1.15,  -- 높음 기준
    low_threshold DECIMAL(3, 2) DEFAULT 0.90,   -- 낮음 기준
    min_days INT DEFAULT 30  -- 평균 계산 기간
);

-- 품목 별칭 테이블
CREATE TABLE item_aliases (
    id SERIAL PRIMARY KEY,
    item_id INT REFERENCES items(id),
    market_id INT REFERENCES markets(id),
    raw_name VARCHAR(200) NOT NULL,  -- 원본 품목명
    confidence DECIMAL(3, 2) DEFAULT 1.0,  -- 매칭 신뢰도
    UNIQUE(market_id, raw_name)
);

-- 인덱스
CREATE INDEX idx_market_prices_item_date ON market_prices(item_id, date DESC);
CREATE INDEX idx_market_prices_market_date ON market_prices(market_id, date DESC);
CREATE INDEX idx_item_aliases_raw_name ON item_aliases(raw_name);
```


### Domain Models (Python)

```python
# app/domain/models.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class PriceTag(Enum):
    HIGH = "높음"
    NORMAL = "보통"
    LOW = "낮음"

@dataclass
class Item:
    id: int
    name_ko: str
    name_en: str
    category: str
    season_start: int
    season_end: int
    default_origin: str
    unit_default: str

@dataclass
class MarketPrice:
    id: int
    item_id: int
    market_id: int
    date: datetime
    price: float
    unit: str
    origin: str
    source: str

@dataclass
class PriceWithTag:
    market_name: str
    price: float
    unit: str
    date: datetime
    tag: PriceTag
    base_price: float
    ratio: float

@dataclass
class ItemDashboard:
    item: Item
    current_prices: List[PriceWithTag]
    price_trend: List[PriceTrendPoint]
    data_sources: List[str]
    is_in_season: bool
```

## Error Handling

### Error Types and Responses

```python
# app/exceptions.py
class AppException(Exception):
    """Base exception"""
    pass

class ItemNotFoundException(AppException):
    """품목을 찾을 수 없음"""
    status_code = 404
    message = "품목을 찾을 수 없습니다"

class PriceDataNotFoundException(AppException):
    """가격 데이터 없음"""
    status_code = 404
    message = "가격 데이터가 없습니다"

class RecognitionFailedException(AppException):
    """이미지 인식 실패"""
    status_code = 400
    message = "품목을 인식할 수 없습니다"

class ExternalAPIException(AppException):
    """외부 API 오류"""
    status_code = 503
    message = "일시적인 오류가 발생했습니다"
```

### Error Handling Strategy

1. **Mobile App**:
   - 네트워크 오류: 재시도 버튼 제공
   - 인식 실패: 직접 검색 유도
   - 데이터 없음: 안내 메시지 표시
   - 모든 오류는 3초 후 자동 숨김

2. **BFF**:
   - 모든 예외를 표준 JSON 포맷으로 변환
   - 5xx 오류는 상세 정보 숨김 (보안)
   - 로그에 전체 스택 트레이스 기록

3. **Core Service**:
   - 비즈니스 로직 오류는 명확한 메시지와 함께 4xx 반환
   - DB 오류는 5xx로 변환
   - 트랜잭션 롤백 처리

4. **Data Ingestion**:
   - 개별 어댑터 실패 시 다른 어댑터 계속 실행
   - 실패 로그 기록 및 Slack 알림 (선택)
   - 3회 연속 실패 시 관리자 알림


## Caching Strategy

### Redis Cache Structure

```
# 품목 검색 결과 (30분 TTL)
items:search:{query} → List<Item>

# 품목 대시보드 (30분 TTL)
items:{item_id}:dashboard:{date} → ItemDashboard

# 당일 가격 (30분 TTL)
prices:{item_id}:{market_id}:today → MarketPrice

# 가격 추이 (1시간 TTL)
prices:{item_id}:trend:{days} → List<PriceTrendPoint>

# 자동완성 (1일 TTL)
autocomplete:{prefix} → List<string>
```

### Cache Invalidation

1. **시간 기반**: TTL 만료 시 자동 삭제
2. **이벤트 기반**: 
   - Data Ingestion 완료 시 해당 품목의 캐시 삭제
   - 품목 정보 수정 시 관련 캐시 삭제

### Cache-Aside Pattern

```python
# BFF에서의 캐시 사용 예시
async def get_item_dashboard(item_id: int, date: datetime):
    cache_key = f"items:{item_id}:dashboard:{date.strftime('%Y%m%d')}"
    
    # 1. 캐시 확인
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 2. Core Service 호출
    data = await core_service.get_dashboard(item_id, date)
    
    # 3. 캐시 저장 (30분)
    await redis.setex(cache_key, 1800, json.dumps(data))
    
    return data
```

## Performance Optimization

### 1. Database Optimization

```sql
-- 파티셔닝: 날짜별로 market_prices 테이블 분할
CREATE TABLE market_prices_2025_11 PARTITION OF market_prices
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- Materialized View: 일별 평균 가격 (차트용)
CREATE MATERIALIZED VIEW daily_avg_prices AS
SELECT 
    item_id,
    market_id,
    date,
    AVG(price) as avg_price,
    COUNT(*) as sample_count
FROM market_prices
GROUP BY item_id, market_id, date;

-- 매일 새벽 갱신
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_avg_prices;
```

### 2. API Response Time Targets

| Endpoint | Target | Strategy |
|----------|--------|----------|
| 품목 검색 | < 200ms | Redis 캐시 + DB 인덱스 |
| 대시보드 | < 500ms | Redis 캐시 + Materialized View |
| 이미지 인식 | < 3s | GPU 추론 + 비동기 처리 |
| 가격 추이 | < 300ms | Materialized View |

### 3. Image Processing Optimization

```python
# 이미지 크기 제한 및 리사이징
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
TARGET_SIZE = (640, 640)  # YOLO 입력 크기

def preprocess_image(image: bytes) -> np.ndarray:
    # 1. 크기 검증
    if len(image) > MAX_IMAGE_SIZE:
        raise ImageTooLargeException()
    
    # 2. 리사이징
    img = Image.open(BytesIO(image))
    img = img.resize(TARGET_SIZE, Image.LANCZOS)
    
    # 3. 정규화
    return np.array(img) / 255.0
```


## Testing Strategy

### 1. Unit Testing

**Mobile App (Flutter)**:
```dart
// Widget 테스트
testWidgets('PriceCard displays correct price and tag', (tester) async {
  await tester.pumpWidget(
    PriceCard(
      market: '가락시장',
      price: 18500,
      unit: 'kg',
      tag: PriceTag.normal,
    ),
  );
  
  expect(find.text('18,500원'), findsOneWidget);
  expect(find.text('보통'), findsOneWidget);
});

// Provider 테스트
test('DashboardProvider fetches data correctly', () async {
  final container = ProviderContainer(
    overrides: [
      apiClientProvider.overrideWithValue(mockApiClient),
    ],
  );
  
  final dashboard = await container.read(dashboardProvider(11).future);
  expect(dashboard.item.name_ko, '광어');
});
```

**Core Service (Python)**:
```python
# 가격 태깅 로직 테스트
def test_price_evaluator_high_tag():
    evaluator = PriceEvaluator(mock_price_repo, mock_rule_repo)
    
    # Base price: 10000, Current: 12000 (ratio: 1.2)
    tag = evaluator.calculate_tag(
        item_id=11,
        market_id=1,
        current_price=12000,
        date=datetime(2025, 11, 10)
    )
    
    assert tag == PriceTag.HIGH

# 별칭 매칭 테스트
def test_alias_matcher_exact_match():
    matcher = AliasMatcher(mock_alias_repo)
    item_id = matcher.match_item("광어(대)", market_id=1)
    assert item_id == 11
```

**ML Service**:
```python
# Detection 테스트
def test_yolo_detector_returns_boxes():
    detector = YOLODetector("models/yolo_detect.pt")
    image = load_test_image("flounder.jpg")
    
    boxes = detector.detect(image)
    
    assert len(boxes) > 0
    assert boxes[0].confidence > 0.5

# Pipeline 통합 테스트
def test_recognition_pipeline_end_to_end():
    pipeline = RecognitionPipeline(detector, classifier)
    image = load_test_image("flounder.jpg")
    
    results = pipeline.recognize(image)
    
    assert len(results) <= 4
    assert results[0].item_name == "광어"
```

### 2. Integration Testing

**API 통합 테스트**:
```python
# BFF → Core Service
@pytest.mark.integration
async def test_get_dashboard_integration():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/items/11/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["item"]["name_ko"] == "광어"
        assert len(data["current_prices"]) > 0
```

**Data Ingestion 테스트**:
```python
@pytest.mark.integration
def test_garak_adapter_fetches_real_data():
    adapter = GarakAdapter(real_api_client)
    data = adapter.fetch_data(datetime.now())
    
    assert len(data) > 0
    assert data[0].price > 0
```

### 3. E2E Testing

**Mobile App E2E (Flutter Integration Test)**:
```dart
testWidgets('Complete flow: search → select → view dashboard', (tester) async {
  await tester.pumpWidget(MyApp());
  
  // 1. 검색
  await tester.enterText(find.byType(SearchBar), '광어');
  await tester.pumpAndSettle();
  
  // 2. 선택
  await tester.tap(find.text('광어'));
  await tester.pumpAndSettle();
  
  // 3. 대시보드 확인
  expect(find.text('가락시장'), findsOneWidget);
  expect(find.byType(PriceChart), findsOneWidget);
});
```

### 4. Performance Testing

```python
# Locust를 사용한 부하 테스트
from locust import HttpUser, task, between

class PriceTrackerUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def search_items(self):
        self.client.get("/api/items?query=광어")
    
    @task(2)
    def get_dashboard(self):
        self.client.get("/api/items/11/dashboard")
    
    @task(1)
    def recognize_image(self):
        with open("test_image.jpg", "rb") as f:
            self.client.post("/api/recognition", files={"image": f})

# 목표: 100 concurrent users, 500ms 평균 응답 시간
```

### 5. Test Coverage Goals

| Component | Target Coverage | Priority Tests |
|-----------|----------------|----------------|
| Core Service | 80% | 가격 태깅, 별칭 매칭 |
| BFF | 70% | API 엔드포인트, 캐싱 |
| ML Service | 60% | Detection, Classification |
| Data Ingestion | 70% | 어댑터, 정규화 |
| Mobile App | 60% | 핵심 UI 플로우 |


## Deployment Architecture

### Container Structure

```yaml
# docker-compose.yml
version: '3.8'

services:
  # BFF
  bff:
    build: ./bff
    ports:
      - "3000:3000"
    environment:
      - REDIS_URL=redis://redis:6379
      - CORE_SERVICE_URL=http://core:8000
      - ML_SERVICE_URL=http://ml:8001
    depends_on:
      - redis
      - core
      - ml

  # Core Service
  core:
    build: ./core-service
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/seafood
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # ML Service
  ml:
    build: ./ml-service
    ports:
      - "8001:8001"
    environment:
      - MODEL_PATH=/models
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Data Ingestion
  ingestion:
    build: ./data-ingestion
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/seafood
      - SCHEDULE_TIMES=08:30,11:30,15:30
    depends_on:
      - postgres

  # PostgreSQL
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=seafood
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
  
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker images
        run: |
          docker build -t seafood/bff:${{ github.sha }} ./bff
          docker build -t seafood/core:${{ github.sha }} ./core-service
          docker build -t seafood/ml:${{ github.sha }} ./ml-service
          docker push seafood/bff:${{ github.sha }}
          docker push seafood/core:${{ github.sha }}
          docker push seafood/ml:${{ github.sha }}
  
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Deploy to production
        run: |
          # Kubernetes 배포 또는 Docker Swarm 업데이트
          kubectl set image deployment/bff bff=seafood/bff:${{ github.sha }}
```

### Mobile App Deployment

```yaml
# Flutter 빌드 및 배포
# .github/workflows/mobile.yml
name: Mobile Build

on:
  push:
    tags: ['mobile-v*']

jobs:
  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - name: Build iOS
        run: |
          cd mobile
          flutter build ios --release
      - name: Upload to TestFlight
        # fastlane 또는 App Store Connect API 사용

  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - name: Build Android
        run: |
          cd mobile
          flutter build apk --release
      - name: Upload to Play Store
        # fastlane 또는 Google Play API 사용
```

## Monitoring and Logging

### Logging Strategy

```python
# 구조화된 로깅 (JSON 포맷)
import structlog

logger = structlog.get_logger()

# 요청 로그
logger.info(
    "api_request",
    method="GET",
    path="/api/items/11/dashboard",
    user_id=123,
    duration_ms=245
)

# 에러 로그
logger.error(
    "recognition_failed",
    error_type="ModelInferenceError",
    item_id=11,
    image_size=1024000,
    stack_trace=traceback.format_exc()
)

# 비즈니스 메트릭
logger.info(
    "price_tag_calculated",
    item_id=11,
    market_id=1,
    tag="HIGH",
    ratio=1.23,
    base_price=10000,
    current_price=12300
)
```

### Metrics Collection

```python
# Prometheus 메트릭
from prometheus_client import Counter, Histogram, Gauge

# API 요청 카운터
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# 응답 시간 히스토그램
api_duration = Histogram(
    'api_duration_seconds',
    'API response time',
    ['endpoint']
)

# 현재 가격 게이지
current_prices = Gauge(
    'item_current_price',
    'Current item price',
    ['item_id', 'market_id']
)

# 인식 성공률
recognition_success_rate = Gauge(
    'recognition_success_rate',
    'Image recognition success rate'
)
```

### Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: seafood_alerts
    rules:
      - alert: HighAPILatency
        expr: api_duration_seconds{quantile="0.95"} > 1.0
        for: 5m
        annotations:
          summary: "API 응답 시간이 1초를 초과했습니다"
      
      - alert: LowRecognitionRate
        expr: recognition_success_rate < 0.7
        for: 10m
        annotations:
          summary: "이미지 인식 성공률이 70% 미만입니다"
      
      - alert: DataIngestionFailed
        expr: increase(ingestion_failures_total[1h]) > 3
        annotations:
          summary: "데이터 수집이 1시간 내 3회 이상 실패했습니다"
```

## Security Considerations

### 1. API Security

```typescript
// BFF에서의 인증/인가 (향후 확장)
@UseGuards(JwtAuthGuard)
@Controller('api/items')
export class ItemsController {
  @Get(':id/dashboard')
  async getDashboard(@Param('id') id: number, @User() user: UserEntity) {
    // Rate limiting: 사용자당 분당 60회
    // API key 검증 (모바일 앱)
  }
}
```

### 2. Data Privacy

- 사용자 검색 기록은 로컬에만 저장 (서버 전송 안 함)
- 업로드된 이미지는 인식 후 즉시 삭제 (저장 안 함)
- 개인정보 없음 (익명 사용 가능)

### 3. Input Validation

```python
# 이미지 업로드 검증
from pydantic import BaseModel, validator

class ImageUploadRequest(BaseModel):
    image: bytes
    
    @validator('image')
    def validate_image(cls, v):
        # 크기 제한
        if len(v) > 5 * 1024 * 1024:
            raise ValueError("Image too large")
        
        # 파일 타입 검증
        if not v.startswith(b'\xff\xd8\xff'):  # JPEG magic number
            raise ValueError("Invalid image format")
        
        return v
```

## Future Enhancements

### Phase 2 Features

1. **농산물/축산물 확장**
   - 새로운 카테고리 추가
   - 별도 ML 모델 학습
   - 시장 데이터 소스 추가

2. **가격 알림**
   - 사용자가 관심 품목 등록
   - 가격이 낮음 태그일 때 푸시 알림
   - Firebase Cloud Messaging 사용

3. **레시피 추천**
   - 제철 품목 기반 레시피 제안
   - 외부 레시피 API 연동

4. **소셜 기능**
   - 사용자 리뷰 및 평점
   - 시장 방문 후기

### Scalability Considerations

- **수평 확장**: 모든 서비스 stateless 설계로 복제 가능
- **DB 샤딩**: 품목 ID 기반 샤딩 (향후 품목 수 증가 시)
- **CDN**: 이미지 및 정적 자산 캐싱
- **Read Replica**: 읽기 부하 분산

