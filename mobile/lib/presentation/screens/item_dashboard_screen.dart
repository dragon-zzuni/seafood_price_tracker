import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../application/providers/dashboard_provider.dart';
import '../../application/providers/settings_provider.dart';
import '../../domain/models/settings.dart';
import '../../domain/models/market_price.dart';
import '../widgets/item_info_card.dart';
import '../widgets/price_card.dart';
import '../widgets/price_chart.dart';
import '../widgets/data_source_footer.dart';
import '../widgets/empty_state_widget.dart';
import '../widgets/loading_indicator.dart';

/// 품목 대시보드 화면
/// 
/// 품목 정보, 가격 카드, 가격 추이 차트, 데이터 출처를 통합하여 표시합니다.
/// pull-to-refresh 기능을 제공합니다.
/// 사용자 설정에 따라 시장 우선 표시 및 가격 단위 변환을 적용합니다.
/// Requirements: 3.1, 4.1, 5.1, 6.5, 12.2, 12.3
class ItemDashboardScreen extends ConsumerWidget {
  final int itemId;
  final String itemName;
  
  const ItemDashboardScreen({
    Key? key,
    required this.itemId,
    required this.itemName,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardState = ref.watch(dashboardProvider(itemId));
    
    return Scaffold(
      appBar: AppBar(
        title: Text(itemName),
        elevation: 0,
      ),
      body: _buildBody(context, ref, dashboardState),
    );
  }
  
  /// 본문 위젯
  Widget _buildBody(BuildContext context, WidgetRef ref, DashboardState state) {
    // 로딩 중
    if (state.isLoading && state.dashboard == null) {
      return const LoadingIndicator(
        message: '데이터를 불러오는 중...',
      );
    }
    
    // 에러 발생 - 네트워크 오류인 경우 재시도 버튼 제공
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
    
    // 데이터 없음
    if (state.dashboard == null) {
      return EmptyStateWidget(
        icon: Icons.inbox_outlined,
        title: '데이터를 불러올 수 없습니다',
        message: '잠시 후 다시 시도해주세요',
        actionLabel: '새로고침',
        onAction: () => _handleRefresh(ref),
      );
    }
    
    // 데이터 표시
    return RefreshIndicator(
      onRefresh: () => _handleRefresh(ref),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 품목 기본 정보
            ItemInfoCard(
              item: state.dashboard!.item,
              isInSeason: state.dashboard!.isInSeason,
            ),
            
            // 가격 정보 섹션
            _buildPriceSection(context, state),
            
            // 가격 추이 차트
            if (state.dashboard!.hasSufficientTrendData)
              PriceChart(
                priceTrend: state.dashboard!.priceTrend,
              )
            else
              Padding(
                padding: const EdgeInsets.all(16),
                child: EmptyStateWidget.insufficientChartData(),
              ),
            
            const SizedBox(height: 16),
            
            // 데이터 출처
            DataSourceFooter(
              dataSources: state.dashboard!.dataSources,
              lastUpdated: _getLastUpdatedDate(state),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 가격 정보 섹션
  /// Requirements: 12.2, 12.3 - 설정된 시장 우선 표시 및 가격 단위 변환 적용
  Widget _buildPriceSection(BuildContext context, DashboardState state) {
    return Consumer(
      builder: (context, ref, child) {
        final dashboard = state.dashboard!;
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 섹션 제목
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
              child: Text(
                '시장별 현재 가격',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            
            // 가격 카드 리스트
            if (dashboard.hasPriceData)
              _buildSortedPriceCards(context, dashboard.currentPrices)
            else
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: EmptyStateWidget.noPrice(
                  onRefresh: () => _handleRefresh(ref),
                ),
              ),
          ],
        );
      },
    );
  }
  
  /// 설정에 따라 정렬된 가격 카드 리스트 생성
  /// Requirements: 12.2 - 우선 표시 시장 설정 적용
  Widget _buildSortedPriceCards(
    BuildContext context,
    List<MarketPrice> prices,
  ) {
    return Consumer(
      builder: (context, ref, child) {
        final marketPreference = ref.watch(marketPreferenceProvider);
        final sortedPrices = _sortPricesByPreference(prices, marketPreference);
        
        return Column(
          children: sortedPrices
              .map((price) => PriceCard(marketPrice: price))
              .toList(),
        );
      },
    );
  }
  
  /// 시장 우선 표시 설정에 따라 가격 리스트 정렬
  List<MarketPrice> _sortPricesByPreference(
    List<MarketPrice> prices,
    MarketPreference preference,
  ) {
    if (preference == MarketPreference.both) {
      // 둘 다 표시: 원래 순서 유지
      return prices;
    }
    
    final sortedPrices = List<MarketPrice>.from(prices);
    
    sortedPrices.sort((a, b) {
      // 우선 시장을 먼저 표시
      final aIsPreferred = _isPreferredMarket(a.market, preference);
      final bIsPreferred = _isPreferredMarket(b.market, preference);
      
      if (aIsPreferred && !bIsPreferred) return -1;
      if (!aIsPreferred && bIsPreferred) return 1;
      
      // 같은 우선순위면 원래 순서 유지
      return 0;
    });
    
    return sortedPrices;
  }
  
  /// 시장이 우선 표시 대상인지 확인
  bool _isPreferredMarket(String marketName, MarketPreference preference) {
    switch (preference) {
      case MarketPreference.garak:
        return marketName.contains('가락');
      case MarketPreference.noryangjin:
        return marketName.contains('노량진');
      case MarketPreference.both:
        return false;
    }
  }
  

  
  /// 새로고침 처리
  Future<void> _handleRefresh(WidgetRef ref) async {
    await ref.read(dashboardProvider(itemId).notifier).refresh(itemId);
  }
  
  /// 최종 업데이트 날짜 추출
  DateTime? _getLastUpdatedDate(DashboardState state) {
    if (state.dashboard == null || !state.dashboard!.hasPriceData) {
      return null;
    }
    
    // 가격 데이터 중 가장 최근 날짜 반환
    final dates = state.dashboard!.currentPrices
        .map((price) => price.dateTime)
        .toList()
      ..sort((a, b) => b.compareTo(a));
    
    return dates.isNotEmpty ? dates.first : null;
  }
}
