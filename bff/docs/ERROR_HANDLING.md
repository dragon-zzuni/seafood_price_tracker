# BFF 에러 핸들링 가이드

## 개요

BFF는 전역 예외 필터(`HttpExceptionFilter`)를 통해 모든 에러를 일관되게 처리하고, 사용자 친화적인 메시지로 변환합니다.

## 요구사항 충족

### Requirement 11.1: 네트워크 오류 처리

네트워크 연결 실패 시 명확한 메시지를 제공합니다.

```typescript
// ECONNREFUSED, ENOTFOUND 에러 처리
{
  "statusCode": 503,
  "message": "네트워크 연결을 확인해주세요",
  "errorType": "ExternalServiceError"
}
```

### Requirement 11.2: 이미지 인식 실패 처리

ML Service의 인식 실패를 사용자 친화적 메시지로 변환합니다.

```typescript
// RecognitionFailedException 처리
{
  "statusCode": 400,
  "message": "품목을 인식할 수 없습니다. 직접 검색해주세요",
  "errorType": "RecognitionFailedException"
}
```

### Requirement 11.3: 서버 오류 보안 처리

5xx 에러는 상세 정보를 숨기고 일반 메시지만 반환합니다.

```typescript
// 500번대 에러 처리
if (status >= 500) {
  message = '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요';
  details = undefined; // 상세 정보 제거
  errorType = 'ServerError'; // 일반적인 타입으로 변경
}
```

## 구현 상세

### 1. HttpExceptionFilter 구조

```typescript
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    // 1. HttpException 처리
    // 2. AxiosError 처리 (Core/ML Service)
    // 3. 기타 예외 처리
    // 4. 5xx 에러 보안 처리
    // 5. 표준 응답 반환
  }
}
```

### 2. 에러 타입별 처리

#### Core Service 에러

| 에러 타입 | HTTP 상태 | 사용자 메시지 |
|----------|----------|-------------|
| `ItemNotFoundException` | 404 | 품목을 찾을 수 없습니다 |
| `PriceDataNotFoundException` | 404 | 가격 데이터가 없습니다 |
| `MarketNotFoundException` | 404 | 시장 정보를 찾을 수 없습니다 |
| `ValidationException` | 400 | 입력 데이터가 올바르지 않습니다 |

#### ML Service 에러

| 에러 타입 | HTTP 상태 | 사용자 메시지 |
|----------|----------|-------------|
| `RecognitionFailedException` | 400 | 품목을 인식할 수 없습니다. 직접 검색해주세요 |
| `ImageTooLargeException` | 400 | 이미지 크기가 너무 큽니다. 5MB 이하의 이미지를 사용해주세요 |
| `InvalidImageFormatException` | 400 | 지원하지 않는 이미지 형식입니다 |
| `ModelInferenceException` | 400 | 품목을 인식할 수 없습니다. 직접 검색해주세요 |

#### 네트워크 에러

| 에러 코드 | HTTP 상태 | 사용자 메시지 |
|----------|----------|-------------|
| `ECONNREFUSED` | 503 | 네트워크 연결을 확인해주세요 |
| `ENOTFOUND` | 503 | 네트워크 연결을 확인해주세요 |
| `ECONNABORTED` | 408 | 요청 시간이 초과되었습니다. 다시 시도해주세요 |

### 3. 응답 형식

모든 에러 응답은 다음 표준 형식을 따릅니다:

```typescript
interface ErrorResponse {
  statusCode: number;      // HTTP 상태 코드
  message: string;         // 사용자 친화적 메시지
  errorType: string;       // 에러 타입 (5xx는 'ServerError'로 통일)
  details?: any;           // 상세 정보 (4xx만 포함, 5xx는 제거)
  timestamp: string;       // ISO 8601 형식
  path: string;           // 요청 경로
}
```

### 4. 로깅 전략

```typescript
// 5xx 에러: ERROR 레벨
if (status >= 500) {
  this.logger.error('Server error:', exception);
}

// 4xx 에러: WARN 레벨
else {
  this.logger.warn(`Client error: ${status} - ${message}`, {
    path: request.url,
    method: request.method,
    errorType,
  });
}
```

## 사용 예제

### 1. 품목 조회 실패

**요청:**
```bash
GET /api/items/99999
```

**응답:**
```json
{
  "statusCode": 404,
  "message": "품목을 찾을 수 없습니다",
  "errorType": "ItemNotFoundException",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/items/99999"
}
```

### 2. 이미지 인식 실패

**요청:**
```bash
POST /api/recognition
Content-Type: multipart/form-data
```

**응답:**
```json
{
  "statusCode": 400,
  "message": "품목을 인식할 수 없습니다. 직접 검색해주세요",
  "errorType": "RecognitionFailedException",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/recognition"
}
```

### 3. 서비스 연결 실패

**요청:**
```bash
GET /api/items/1/dashboard
```

**응답 (Core Service 다운 시):**
```json
{
  "statusCode": 503,
  "message": "네트워크 연결을 확인해주세요",
  "errorType": "ExternalServiceError",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/items/1/dashboard"
}
```

### 4. 서버 내부 오류

**요청:**
```bash
GET /api/items/1
```

**응답 (서버 에러 발생 시):**
```json
{
  "statusCode": 500,
  "message": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요",
  "errorType": "ServerError",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "path": "/api/items/1"
}
```

**주의:** 5xx 에러는 `details`, `stack` 등의 상세 정보가 제거됩니다.

## 테스트

### 단위 테스트

```bash
npm test http-exception.filter
```

테스트 파일: `src/common/filters/http-exception.filter.spec.ts`

**테스트 케이스:**
- HttpException 처리
- Axios 에러 처리 (Core/ML Service)
- 네트워크 에러 처리
- 5xx 에러 보안 처리
- 응답 형식 검증

### E2E 테스트

```bash
npm run test:e2e error-handling
```

테스트 파일: `test/error-handling.e2e-spec.ts`

**테스트 시나리오:**
- 존재하지 않는 품목 조회
- 이미지 인식 실패
- 서비스 연결 실패
- 서버 에러 발생

## 확장 가이드

### 새로운 에러 타입 추가

1. `translateErrorMessage()` 메서드에 번역 추가:

```typescript
private translateErrorMessage(errorType: string, originalMessage: string): string {
  const translations: Record<string, string> = {
    // 기존 번역...
    'NewErrorType': '새로운 에러 메시지',
  };
  
  return translations[errorType] || originalMessage;
}
```

2. 테스트 케이스 추가:

```typescript
it('새로운 에러 타입을 변환해야 함', () => {
  const axiosError = {
    isAxiosError: true,
    response: {
      status: 400,
      data: {
        error: {
          type: 'NewErrorType',
          message: 'Original message',
        },
      },
    },
  } as AxiosError;
  
  filter.catch(axiosError, mockHost);
  
  expect(mockResponse.json).toHaveBeenCalledWith(
    expect.objectContaining({
      message: '새로운 에러 메시지',
    })
  );
});
```

## 모니터링

### 로그 확인

```bash
# 에러 로그 필터링
grep "ERROR" logs/bff.log

# 특정 에러 타입 검색
grep "ItemNotFoundException" logs/bff.log
```

### 메트릭

다음 메트릭을 모니터링하는 것을 권장합니다:

- 4xx 에러 비율
- 5xx 에러 비율
- 네트워크 에러 빈도
- 에러 타입별 분포

## 참고 자료

- [NestJS Exception Filters](https://docs.nestjs.com/exception-filters)
- [Axios Error Handling](https://axios-http.com/docs/handling_errors)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
