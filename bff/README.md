# BFF (Backend For Frontend) - Seafood Price Tracker

수산물 가격 추적 시스템의 API Gateway 서비스입니다.

## 기능

- **품목 검색**: 자동완성 기능을 제공하는 품목 검색
- **품목 대시보드**: 품목 정보, 가격, 추이를 통합한 대시보드 API
- **이미지 인식**: ML Service를 통한 이미지 인식 프록시
- **캐싱**: Redis를 활용한 Cache-Aside 패턴 구현

## 기술 스택

- **Framework**: NestJS 10.x
- **Language**: TypeScript
- **Cache**: Redis
- **HTTP Client**: Axios
- **Documentation**: Swagger/OpenAPI

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 설정합니다:

```env
REDIS_URL=redis://localhost:6379
CORE_SERVICE_URL=http://localhost:8000
ML_SERVICE_URL=http://localhost:8001
```

### 3. 개발 모드 실행

```bash
npm run start:dev
```

### 4. 프로덕션 빌드

```bash
npm run build
npm start
```

## API 엔드포인트

### 품목 관련

- `GET /api/items?query={query}` - 품목 검색 (자동완성)
- `GET /api/items/:id` - 품목 상세 조회
- `GET /api/items/:id/dashboard` - 품목 대시보드 조회

### 이미지 인식

- `POST /api/recognition` - 이미지 업로드 및 인식
  - **Request**: `multipart/form-data` (필드명: `image`)
  - **Response**: 최대 4개의 품목 후보 (신뢰도 순)
  - **제약사항**: 최대 5MB, JPEG/PNG 형식

### 가격 관련

- `GET /api/prices/markets` - 시장 목록 조회

## API 문서

서버 실행 후 다음 URL에서 Swagger 문서를 확인할 수 있습니다:

```
http://localhost:3000/api/docs
```

### 이미지 인식 API 예제

**요청:**

```bash
curl -X POST http://localhost:3000/api/recognition \
  -F "image=@flounder.jpg"
```

**성공 응답 (200):**

```json
{
  "candidates": [
    {
      "item_id": 11,
      "item_name": "광어",
      "confidence": 0.85
    },
    {
      "item_id": 23,
      "item_name": "넙치",
      "confidence": 0.72
    },
    {
      "item_id": 45,
      "item_name": "도다리",
      "confidence": 0.58
    }
  ]
}
```

**실패 응답 (400):**

```json
{
  "statusCode": 400,
  "message": "품목을 인식할 수 없습니다. 직접 검색해주세요",
  "timestamp": "2025-11-10T12:00:00.000Z"
}
```

**서비스 오류 (503):**

```json
{
  "statusCode": 503,
  "message": "이미지 인식 서비스에 일시적인 오류가 발생했습니다",
  "timestamp": "2025-11-10T12:00:00.000Z"
}
```

## 아키텍처

### 모듈 구조

```
src/
├── common/              # 공통 유틸리티
│   ├── types.ts        # 타입 정의
│   ├── http-client.service.ts  # HTTP 클라이언트
│   └── filters/        # 예외 필터
├── cache/              # Redis 캐싱
│   ├── cache.module.ts
│   └── cache.service.ts
├── items/              # 품목 관련
│   ├── items.module.ts
│   ├── items.controller.ts
│   └── items.service.ts
├── prices/             # 가격 관련
│   ├── prices.module.ts
│   ├── prices.controller.ts
│   └── prices.service.ts
└── recognition/        # 이미지 인식
    ├── recognition.module.ts
    ├── recognition.controller.ts
    └── recognition.service.ts
```

### 캐싱 전략

- **Cache-Aside 패턴**: 캐시 미스 시 원본 데이터 조회 후 캐시 저장
- **TTL 설정**:
  - 품목 검색: 30분
  - 대시보드: 30분
  - 시장 목록: 1시간

### 캐시 키 전략

```
items:search:{query}              # 품목 검색 결과
items:{id}                        # 품목 상세
items:{id}:dashboard:{date}       # 대시보드 데이터
markets:list                      # 시장 목록
```

## 에러 처리

BFF는 전역 예외 필터(`HttpExceptionFilter`)를 통해 모든 에러를 일관되게 처리합니다.

### 에러 응답 형식

모든 에러 응답은 다음 표준 형식을 따릅니다:

```json
{
  "statusCode": 404,
  "message": "품목을 찾을 수 없습니다",
  "errorType": "ItemNotFoundException",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/items/99999"
}
```

### 에러 처리 전략

#### 1. Core/ML Service 에러 변환 (Requirement 11.2)

외부 서비스의 에러를 사용자 친화적인 한글 메시지로 자동 변환합니다:

| 원본 에러 타입 | 변환된 메시지 |
|--------------|-------------|
| `ItemNotFoundException` | 품목을 찾을 수 없습니다 |
| `PriceDataNotFoundException` | 가격 데이터가 없습니다 |
| `RecognitionFailedException` | 품목을 인식할 수 없습니다. 직접 검색해주세요 |
| `ImageTooLargeException` | 이미지 크기가 너무 큽니다. 5MB 이하의 이미지를 사용해주세요 |

#### 2. 네트워크 에러 처리 (Requirement 11.1)

서비스 연결 실패 시 명확한 메시지를 제공합니다:

```json
{
  "statusCode": 503,
  "message": "네트워크 연결을 확인해주세요",
  "errorType": "ExternalServiceError",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/items/1"
}
```

**처리되는 네트워크 에러:**
- `ECONNREFUSED`: 서비스 연결 거부
- `ENOTFOUND`: 서비스 주소를 찾을 수 없음
- `ECONNABORTED`: 요청 타임아웃

#### 3. 5xx 에러 보안 처리 (Requirement 11.3)

서버 에러(500번대)는 상세 정보를 숨기고 일반적인 메시지만 반환합니다:

```json
{
  "statusCode": 500,
  "message": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요",
  "errorType": "ServerError",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/items/1"
}
```

**보안 조치:**
- 스택 트레이스 제거
- 상세 에러 정보 제거
- 내부 구현 정보 숨김
- 서버 로그에만 전체 에러 기록

#### 4. 4xx 클라이언트 에러

클라이언트 에러는 명확한 메시지와 함께 반환됩니다:

```json
{
  "statusCode": 400,
  "message": "입력 데이터가 올바르지 않습니다",
  "errorType": "ValidationException",
  "details": {
    "field": "query",
    "constraint": "minLength"
  },
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/items"
}
```

### 에러 로깅

- **5xx 에러**: `ERROR` 레벨로 전체 스택 트레이스 기록
- **4xx 에러**: `WARN` 레벨로 요청 정보와 함께 기록
- **네트워크 에러**: `ERROR` 레벨로 연결 실패 정보 기록

### 테스트

에러 핸들링 테스트는 다음 파일에서 확인할 수 있습니다:

- 단위 테스트: `src/common/filters/http-exception.filter.spec.ts`
- 통합 테스트: `test/error-handling.e2e-spec.ts`

```bash
# 단위 테스트 실행
npm test http-exception.filter

# E2E 테스트 실행
npm run test:e2e error-handling
```

## 개발

### 코드 스타일

```bash
npm run lint
```

### 테스트

```bash
npm test
```

## Docker

### 이미지 빌드

```bash
docker build -t seafood-bff .
```

### 컨테이너 실행

```bash
docker run -p 3000:3000 \
  -e REDIS_URL=redis://redis:6379 \
  -e CORE_SERVICE_URL=http://core:8000 \
  -e ML_SERVICE_URL=http://ml:8001 \
  seafood-bff
```

## 의존 서비스

- **Core Service**: 품목 및 가격 데이터 제공
- **ML Service**: 이미지 인식 기능 제공
- **Redis**: 캐싱 레이어

## 성능 목표

- 품목 검색: < 200ms
- 대시보드 조회: < 500ms
- 이미지 인식: < 3s

## 라이선스

MIT
