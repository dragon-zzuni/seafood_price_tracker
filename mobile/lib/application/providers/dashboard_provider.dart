import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/item_dashboard.dart';
import '../../infrastructure/api_client.dart';
import 'item_provider.dart';

/// 대시보드 데이터 상태
class DashboardState {
  final ItemDashboard? dashboard;
  final bool isLoading;
  final String? error;
  
  DashboardState({
    this.dashboard,
    this.isLoading = false,
    this.error,
  });
  
  DashboardState copyWith({
    ItemDashboard? dashboard,
    bool? isLoading,
    String? error,
  }) {
    return DashboardState(
      dashboard: dashboard ?? this.dashboard,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// 대시보드 데이터 Provider (Riverpod)
/// 
/// BFF에서 대시보드 데이터를 조회하고 로딩 및 에러 상태를 관리합니다.
/// Requirements: 3.1, 4.1, 6.5, 11.4
class DashboardNotifier extends StateNotifier<DashboardState> {
  final ApiClient _apiClient;
  
  DashboardNotifier(this._apiClient) : super(DashboardState());
  
  /// 품목 대시보드 데이터 로드
  Future<void> loadDashboard(int itemId, {DateTime? date}) async {
    // 로딩 상태 시작
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      // 쿼리 파라미터 구성
      final queryParams = <String, dynamic>{};
      if (date != null) {
        queryParams['date'] = date.toIso8601String().split('T')[0]; // YYYY-MM-DD
      }
      
      // BFF API 호출
      final response = await _apiClient.get(
        '/items/$itemId/dashboard',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );
      
      // 응답 파싱
      final data = response.data;
      final dashboard = ItemDashboard.fromJson(data as Map<String, dynamic>);
      
      // 성공 상태 업데이트
      state = DashboardState(
        dashboard: dashboard,
        isLoading: false,
        error: null,
      );
    } on ApiException catch (e) {
      // API 예외 처리
      state = DashboardState(
        dashboard: null,
        isLoading: false,
        error: e.message,
      );
    } catch (e) {
      // 기타 예외 처리
      state = DashboardState(
        dashboard: null,
        isLoading: false,
        error: '데이터를 불러오는 중 오류가 발생했습니다',
      );
    }
  }
  
  /// 대시보드 새로고침
  Future<void> refresh(int itemId) async {
    await loadDashboard(itemId);
  }
  
  /// 상태 초기화
  void clear() {
    state = DashboardState();
  }
}

/// 대시보드 Provider (품목 ID별로 독립적인 인스턴스)
final dashboardProvider = StateNotifierProvider.family<DashboardNotifier, DashboardState, int>(
  (ref, itemId) {
    final apiClient = ref.watch(apiClientProvider);
    final notifier = DashboardNotifier(apiClient);
    
    // Provider 생성 시 자동으로 데이터 로드
    notifier.loadDashboard(itemId);
    
    return notifier;
  },
);
