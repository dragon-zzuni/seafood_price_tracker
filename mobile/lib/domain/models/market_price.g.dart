// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'market_price.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MarketPrice _$MarketPriceFromJson(Map<String, dynamic> json) => MarketPrice(
      market: json['market'] as String,
      price: (json['price'] as num).toDouble(),
      unit: json['unit'] as String,
      date: json['date'] as String,
      tag: $enumDecode(_$PriceTagEnumMap, json['tag']),
      basePrice: (json['base_price'] as num?)?.toDouble(),
      ratio: (json['ratio'] as num?)?.toDouble(),
      origin: json['origin'] as String?,
    );

Map<String, dynamic> _$MarketPriceToJson(MarketPrice instance) =>
    <String, dynamic>{
      'market': instance.market,
      'price': instance.price,
      'unit': instance.unit,
      'date': instance.date,
      'tag': _$PriceTagEnumMap[instance.tag]!,
      'base_price': instance.basePrice,
      'ratio': instance.ratio,
      'origin': instance.origin,
    };

const _$PriceTagEnumMap = {
  PriceTag.high: '높음',
  PriceTag.normal: '보통',
  PriceTag.low: '낮음',
};
