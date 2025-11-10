# 에러 처리 가이드

## 개요

모바일 앱의 에러 처리는 사용자 친화적인 메시지와 적절한 UI 피드백을 제공하여 사용자 경험을 향상시킵니다.

## 에러 UI 컴포넌트

### 1. ErrorSnackbar

**용도**: 일시적인 에러 메시지 표시 (3초 자동 숨김)

**사용 예시**:
```dart
// 네트워크 오류
ErrorSnackbar.show(
  context,
  AppError(
    type: ErrorType.network,
    message: '네트워크 연결을 확인해주세요',
    canRetry: true,
  ),
  onRetry: () => _handleRetry(),
);

// 인식 실패
ErrorSnackbar.show(
  context,
  AppError(
    type: ErrorType.recognition,
    message: '품목을 인식할 수 없습니다. 직접 검색해주세요',
    canRetry: false,
  ),
);

// 간단한 메시지
ErrorSnackbar.showMessage(
  context,
  '일시적인 오류가 발생했습니다',
  isError: true,
);
```

**특징**:
- 3초 후 자동 숨김
- 에러 타입별 색상 구분
- 재시도 버튼 옵션 제공
- 아이콘 자동 선택

### 2. EmptyStateWidget

**용도**: 데이터가 없거나 에러 상태를 전체 화면으로 표시

**팩토리 메서드**:

```dart
// 가격 데이터 없음
EmptyStateWidget.noPrice(
  onRefresh: () => _handleRefresh(),
)

// 검색 결과 없음
EmptyStateWidget.noSearchResults(
  query: '광어',
)

// 인식 실패 (직접 검색 유도)
EmptyStateWidget.recognitionFailed(
  onSearchManually: () => Navigator.pop(context),
)

// 차트 데이터 부족
EmptyStateWidget.insufficientChartData()

// 네트워크 오류
EmptyStateWidget.networkError(
  onRetry: () => _handleRetry(),
)

// 커스텀 에러
EmptyStateWidget(
  icon: Icons.error_outline,
  title: '오류가 발생했습니다',
  message: '잠시 후 다시 시도해주세요',
  actionLabel: '재시도',
  onAction: () => _handleRetry(),
)
```

### 3. LoadingIndicator

**용도**: 데이터 로딩 중 표시

**사용 예시**:
```dart
// 기본 로딩
LoadingIndicator(
  message: '데이터를 불러오는 중...',
)

// 이미지 인식 프로그레스
RecognitionProgressIndicator(
  progress: 0.5, // 0.0 ~ 1.0
  message: '이미지를 분석하고 있습니다...',
)

// 오버레이 형태
LoadingOverlay(
  isLoading: isLoading,
  message: '처리 중...',
  child: YourContentWidget(),
)
```

## 에러 타입 및 메시지

### ErrorType 정의

```dart
enum ErrorType {
  network,      // 네트워크 연결 오류
  notFound,     // 데이터를 찾을 수 없음
  validation,   // 입력 데이터 검증 실패
  recognition,  // 이미지 인식 실패
  server,       // 서버 오류 (5xx)
  timeout,      // 요청 시간 초과
  unknown,      // 알 수 없는 오류
}
```

### 표준 에러 메시지

| 에러 타입 | 메시지 | 재시도 가능 |
|----------|--------|-----------|
| network | 네트워크 연결을 확인해주세요 | ✅ |
| notFound | 요청한 정보를 찾을 수 없습니다 | ❌ |
| validation | 입력 데이터가 올바르지 않습니다 | ❌ |
| recognition | 품목을 인식할 수 없습니다. 직접 검색해주세요 | ❌ |
| server | 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요 | ✅ |
| timeout | 요청 시간이 초과되었습니다. 다시 시도해주세요 | ✅ |
| unknown | 알 수 없는 오류가 발생했습니다 | ❌ |

## 화면별 에러 처리

### HomeScreen

**검색 에러**:
- Provider의 error 상태 변경 감지
- ErrorSnackbar로 3초간 표시
- 자동으로 숨김

**이미지 인식 에러**:
- LoadingIndicator로 진행 상태 표시
- 실패 시 ErrorSnackbar 표시
- 인식 실패 시 직접 검색 유도 메시지

```dart
// 에러 리스너 설정
ref.listen<ItemSearchState>(
  itemSearchProvider,
  (previous, next) {
    if (next.error != null && next.error != previous?.error) {
      ErrorSnackbar.show(
        context,
        AppError(
          type: ErrorType.unknown,
          message: next.error!,
          canRetry: false,
        ),
      );
    }
  },
);
```

### ItemDashboardScreen

**데이터 로딩 실패**:
- 네트워크 오류: EmptyStateWidget.networkError (재시도 버튼)
- 기타 오류: EmptyStateWidget (재시도 버튼)

**가격 데이터 없음**:
- EmptyStateWidget.noPrice (새로고침 버튼)

**차트 데이터 부족**:
- EmptyStateWidget.insufficientChartData

```dart
// 에러 상태 처리
if (state.error != null && state.dashboard == null) {
  final isNetworkError = state.error!.contains('네트워크') || 
                         state.error!.contains('연결');
  
  return isNetworkError
      ? EmptyStateWidget.networkError(
          onRetry: () => _handleRefresh(ref),
        )
      : EmptyStateWidget(
          icon: Icons.error_outline,
          title: '오류가 발생했습니다',
          message: state.error,
          actionLabel: '재시도',
          onAction: () => _handleRefresh(ref),
        );
}
```

### RecognitionResultScreen

**인식 결과 없음**:
- EmptyStateWidget.recognitionFailed
- "직접 검색하기" 버튼으로 홈 화면 복귀

```dart
Widget _buildEmptyState(BuildContext context) {
  return EmptyStateWidget.recognitionFailed(
    onSearchManually: () {
      Navigator.of(context).pop();
    },
  );
}
```

## Provider 에러 처리 패턴

### 표준 에러 처리 흐름

```dart
class YourNotifier extends StateNotifier<YourState> {
  Future<void> loadData() async {
    // 1. 로딩 상태 시작
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      // 2. API 호출
      final response = await _apiClient.get('/endpoint');
      
      // 3. 성공 상태 업데이트
      state = state.copyWith(
        data: parseResponse(response),
        isLoading: false,
        error: null,
      );
    } on ApiException catch (e) {
      // 4. API 예외 처리
      state = state.copyWith(
        isLoading: false,
        error: e.message,
      );
    } catch (e) {
      // 5. 기타 예외 처리
      state = state.copyWith(
        isLoading: false,
        error: '데이터를 불러오는 중 오류가 발생했습니다',
      );
    }
  }
}
```

## 베스트 프랙티스

### 1. 에러 메시지는 사용자 친화적으로

❌ 나쁜 예:
```dart
error: 'DioException: Connection timeout'
```

✅ 좋은 예:
```dart
error: '네트워크 연결을 확인해주세요'
```

### 2. 재시도 옵션 제공

네트워크 오류, 서버 오류, 타임아웃 등 일시적인 오류는 재시도 버튼을 제공합니다.

```dart
ErrorSnackbar.show(
  context,
  AppError(
    type: ErrorType.network,
    message: '네트워크 연결을 확인해주세요',
    canRetry: true,
  ),
  onRetry: () => _handleRetry(),
);
```

### 3. 로딩 상태 명확히 표시

```dart
// 전체 화면 로딩
if (state.isLoading && state.data == null) {
  return LoadingIndicator(message: '데이터를 불러오는 중...');
}

// 부분 로딩 (새로고침)
RefreshIndicator(
  onRefresh: () => _handleRefresh(),
  child: YourContent(),
)
```

### 4. 에러 상태 초기화

재시도 시 이전 에러 상태를 초기화합니다.

```dart
Future<void> retry() async {
  state = state.copyWith(error: null, isLoading: true);
  await loadData();
}
```

### 5. 3초 자동 숨김 스낵바

일시적인 에러 메시지는 3초 후 자동으로 숨깁니다.

```dart
ErrorSnackbar.show(
  context,
  error,
  // duration은 자동으로 3초로 설정됨
);
```

## 테스트 가이드

### 에러 시나리오 테스트

1. **네트워크 오류**: 비행기 모드 활성화
2. **서버 오류**: BFF 서버 중지
3. **타임아웃**: 느린 네트워크 시뮬레이션
4. **인식 실패**: 불명확한 이미지 업로드
5. **데이터 없음**: 존재하지 않는 품목 ID 조회

### 테스트 체크리스트

- [ ] 에러 메시지가 사용자 친화적인가?
- [ ] 3초 후 스낵바가 자동으로 숨겨지는가?
- [ ] 재시도 버튼이 정상 작동하는가?
- [ ] 로딩 인디케이터가 적절히 표시되는가?
- [ ] 에러 상태에서 앱이 크래시하지 않는가?

## Requirements 매핑

- **11.1**: 네트워크 오류 메시지 및 재시도 버튼
- **11.2**: 인식 실패 시 직접 검색 유도
- **11.3**: 서버 오류 메시지
- **11.4**: 로딩 인디케이터
- **11.5**: 3초 자동 숨김 스낵바
