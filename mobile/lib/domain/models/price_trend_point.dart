import 'package:json_annotation/json_annotation.dart';

part 'price_trend_point.g.dart';

/// 가격 추이 데이터 포인트
/// Requirements: 5.1, 5.2
@JsonSerializable()
class PriceTrendPoint {
  /// 날짜 (ISO 8601 형식)
  final String date;
  
  /// 시장명
  final String market;
  
  /// 가격
  final double price;
  
  PriceTrendPoint({
    required this.date,
    required this.market,
    required this.price,
  });
  
  factory PriceTrendPoint.fromJson(Map<String, dynamic> json) => 
      _$PriceTrendPointFromJson(json);
  
  Map<String, dynamic> toJson() => _$PriceTrendPointToJson(this);
  
  /// 날짜를 DateTime으로 변환
  DateTime get dateTime => DateTime.parse(date);
}
