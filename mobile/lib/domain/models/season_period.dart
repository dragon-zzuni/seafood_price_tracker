import 'package:json_annotation/json_annotation.dart';

part 'season_period.g.dart';

/// 제철 기간 모델
/// Requirements: 3.3, 3.4, 3.5
@JsonSerializable()
class SeasonPeriod {
  /// 시작 월 (1-12)
  final int from;
  
  /// 종료 월 (1-12)
  final int to;
  
  SeasonPeriod({
    required this.from,
    required this.to,
  });
  
  factory SeasonPeriod.fromJson(Map<String, dynamic> json) => 
      _$SeasonPeriodFromJson(json);
  
  Map<String, dynamic> toJson() => _$SeasonPeriodToJson(this);
  
  /// 현재가 제철인지 확인
  bool isInSeason([DateTime? date]) {
    final now = date ?? DateTime.now();
    final currentMonth = now.month;
    
    // 제철 기간이 연도를 넘어가는 경우 (예: 11월~2월)
    if (from > to) {
      return currentMonth >= from || currentMonth <= to;
    }
    
    // 일반적인 경우
    return currentMonth >= from && currentMonth <= to;
  }
  
  /// 제철 기간을 문자열로 반환 (예: "11월~2월")
  String get displayText => '$from월~$to월';
}
