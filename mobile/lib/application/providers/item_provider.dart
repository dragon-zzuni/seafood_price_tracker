import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/models.dart';
import '../../infrastructure/api_client.dart';

/// API 클라이언트 Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// 품목 검색 상태
class ItemSearchState {
  final List<Item> items;
  final bool isLoading;
  final String? error;
  final String query;
  final String? selectedCategory;
  
  ItemSearchState({
    this.items = const [],
    this.isLoading = false,
    this.error,
    this.query = '',
    this.selectedCategory,
  });
  
  ItemSearchState copyWith({
    List<Item>? items,
    bool? isLoading,
    String? error,
    String? query,
    String? selectedCategory,
  }) {
    return ItemSearchState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      query: query ?? this.query,
      selectedCategory: selectedCategory ?? this.selectedCategory,
    );
  }
}

/// 품목 검색 Provider (Riverpod)
/// 
/// 검색 쿼리 디바운싱(300ms), 로딩 상태, 에러 처리를 담당합니다.
/// Requirements: 2.1, 2.2, 11.1
class ItemSearchNotifier extends StateNotifier<ItemSearchState> {
  final ApiClient _apiClient;
  Timer? _debounceTimer;
  
  static const Duration debounceDuration = Duration(milliseconds: 300);
  
  ItemSearchNotifier(this._apiClient) : super(ItemSearchState());
  
  /// 검색 쿼리 업데이트 (디바운싱 적용)
  void updateQuery(String query) {
    // 이전 타이머 취소
    _debounceTimer?.cancel();
    
    // 쿼리 상태 즉시 업데이트
    state = state.copyWith(query: query, error: null);
    
    // 빈 쿼리면 결과 초기화
    if (query.trim().isEmpty) {
      state = state.copyWith(items: [], isLoading: false);
      return;
    }
    
    // 로딩 상태 표시
    state = state.copyWith(isLoading: true);
    
    // 300ms 후 검색 실행
    _debounceTimer = Timer(debounceDuration, () {
      _performSearch(query, state.selectedCategory);
    });
  }
  
  /// 카테고리 필터 변경
  void updateCategory(String? category) {
    state = state.copyWith(selectedCategory: category, error: null);
    
    // 현재 쿼리가 있으면 즉시 재검색
    if (state.query.trim().isNotEmpty) {
      state = state.copyWith(isLoading: true);
      _performSearch(state.query, category);
    }
  }
  
  /// 실제 검색 수행
  Future<void> _performSearch(String query, String? category) async {
    try {
      final queryParams = <String, dynamic>{
        'query': query,
      };
      
      if (category != null) {
        queryParams['category'] = category;
      }
      
      final response = await _apiClient.get(
        '/items',
        queryParameters: queryParams,
      );
      
      // 응답 파싱
      final data = response.data;
      final List<dynamic> itemsJson = data['items'] ?? [];
      final items = itemsJson
          .map((json) => Item.fromJson(json as Map<String, dynamic>))
          .toList();
      
      // 최대 10개로 제한 (Requirements: 2.2)
      final limitedItems = items.take(10).toList();
      
      state = state.copyWith(
        items: limitedItems,
        isLoading: false,
        error: null,
      );
    } on ApiException catch (e) {
      state = state.copyWith(
        items: [],
        isLoading: false,
        error: e.message,
      );
    } catch (e) {
      state = state.copyWith(
        items: [],
        isLoading: false,
        error: '알 수 없는 오류가 발생했습니다',
      );
    }
  }
  
  /// 검색 결과 초기화
  void clear() {
    _debounceTimer?.cancel();
    state = ItemSearchState();
  }
  
  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }
}

/// 품목 검색 Provider
final itemSearchProvider = StateNotifierProvider<ItemSearchNotifier, ItemSearchState>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return ItemSearchNotifier(apiClient);
});

/// 선택된 품목 Provider
final selectedItemProvider = StateProvider<Item?>((ref) => null);
