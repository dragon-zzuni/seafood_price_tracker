// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'price_trend_point.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PriceTrendPoint _$PriceTrendPointFromJson(Map<String, dynamic> json) =>
    PriceTrendPoint(
      date: json['date'] as String,
      market: json['market'] as String,
      price: (json['price'] as num).toDouble(),
    );

Map<String, dynamic> _$PriceTrendPointToJson(PriceTrendPoint instance) =>
    <String, dynamic>{
      'date': instance.date,
      'market': instance.market,
      'price': instance.price,
    };
