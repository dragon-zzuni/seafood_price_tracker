import 'package:json_annotation/json_annotation.dart';
import 'item_detail.dart';
import 'market_price.dart';
import 'price_trend_point.dart';

part 'item_dashboard.g.dart';

/// 품목 대시보드 통합 모델
/// Requirements: 3.1, 4.1, 5.1, 6.5
@JsonSerializable()
class ItemDashboard {
  /// 품목 기본 정보
  final ItemDetail item;
  
  /// 현재 시장별 가격 리스트
  @JsonKey(name: 'current_prices')
  final List<MarketPrice> currentPrices;
  
  /// 가격 추이 데이터
  @JsonKey(name: 'price_trend')
  final PriceTrend priceTrend;
  
  /// 데이터 출처 리스트
  @JsonKey(name: 'data_sources')
  final List<String> dataSources;
  
  /// 제철 여부
  @JsonKey(name: 'is_in_season')
  final bool isInSeason;
  
  ItemDashboard({
    required this.item,
    required this.currentPrices,
    required this.priceTrend,
    required this.dataSources,
    required this.isInSeason,
  });
  
  factory ItemDashboard.fromJson(Map<String, dynamic> json) => 
      _$ItemDashboardFromJson(json);
  
  Map<String, dynamic> toJson() => _$ItemDashboardToJson(this);
  
  /// 데이터 출처를 쉼표로 구분된 문자열로 반환
  String get dataSourcesText => dataSources.join(', ');
  
  /// 가격 데이터가 있는지 확인
  bool get hasPriceData => currentPrices.isNotEmpty;
  
  /// 추이 데이터가 충분한지 확인 (최소 3개)
  bool get hasSufficientTrendData => priceTrend.data.length >= 3;
}

/// 가격 추이 정보
@JsonSerializable()
class PriceTrend {
  /// 기간 (일 단위)
  @JsonKey(name: 'period_days')
  final int periodDays;
  
  /// 추이 데이터 포인트 리스트
  final List<PriceTrendPoint> data;
  
  PriceTrend({
    required this.periodDays,
    required this.data,
  });
  
  factory PriceTrend.fromJson(Map<String, dynamic> json) => 
      _$PriceTrendFromJson(json);
  
  Map<String, dynamic> toJson() => _$PriceTrendToJson(this);
  
  /// 시장별로 데이터 그룹화
  Map<String, List<PriceTrendPoint>> get groupedByMarket {
    final Map<String, List<PriceTrendPoint>> grouped = {};
    
    for (final point in data) {
      if (!grouped.containsKey(point.market)) {
        grouped[point.market] = [];
      }
      grouped[point.market]!.add(point);
    }
    
    return grouped;
  }
  
  /// 최소 가격
  double get minPrice {
    if (data.isEmpty) return 0;
    return data.map((p) => p.price).reduce((a, b) => a < b ? a : b);
  }
  
  /// 최대 가격
  double get maxPrice {
    if (data.isEmpty) return 0;
    return data.map((p) => p.price).reduce((a, b) => a > b ? a : b);
  }
}
