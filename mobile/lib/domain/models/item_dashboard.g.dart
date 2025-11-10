// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'item_dashboard.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ItemDashboard _$ItemDashboardFromJson(Map<String, dynamic> json) =>
    ItemDashboard(
      item: ItemDetail.fromJson(json['item'] as Map<String, dynamic>),
      currentPrices: (json['current_prices'] as List<dynamic>)
          .map((e) => MarketPrice.fromJson(e as Map<String, dynamic>))
          .toList(),
      priceTrend:
          PriceTrend.fromJson(json['price_trend'] as Map<String, dynamic>),
      dataSources: (json['data_sources'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      isInSeason: json['is_in_season'] as bool,
    );

Map<String, dynamic> _$ItemDashboardToJson(ItemDashboard instance) =>
    <String, dynamic>{
      'item': instance.item,
      'current_prices': instance.currentPrices,
      'price_trend': instance.priceTrend,
      'data_sources': instance.dataSources,
      'is_in_season': instance.isInSeason,
    };

PriceTrend _$PriceTrendFromJson(Map<String, dynamic> json) => PriceTrend(
      periodDays: (json['period_days'] as num).toInt(),
      data: (json['data'] as List<dynamic>)
          .map((e) => PriceTrendPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$PriceTrendToJson(PriceTrend instance) =>
    <String, dynamic>{
      'period_days': instance.periodDays,
      'data': instance.data,
    };
