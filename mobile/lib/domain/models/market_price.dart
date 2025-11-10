import 'package:json_annotation/json_annotation.dart';
import 'price_tag.dart';

part 'market_price.g.dart';

/// 시장별 가격 정보 모델
/// Requirements: 4.1, 4.2, 6.5
@JsonSerializable()
class MarketPrice {
  /// 시장명 (예: "가락시장", "노량진수산시장")
  final String market;
  
  /// 가격
  final double price;
  
  /// 단위 (예: "kg", "마리", "상자")
  final String unit;
  
  /// 가격 수집 날짜 (ISO 8601 형식)
  final String date;
  
  /// 가격 태그 (높음/보통/낮음)
  final PriceTag tag;
  
  /// 기준 가격 (최근 30일 평균)
  @JsonKey(name: 'base_price')
  final double? basePrice;
  
  /// 기준 가격 대비 비율
  final double? ratio;
  
  /// 산지 정보
  final String? origin;
  
  MarketPrice({
    required this.market,
    required this.price,
    required this.unit,
    required this.date,
    required this.tag,
    this.basePrice,
    this.ratio,
    this.origin,
  });
  
  factory MarketPrice.fromJson(Map<String, dynamic> json) => 
      _$MarketPriceFromJson(json);
  
  Map<String, dynamic> toJson() => _$MarketPriceToJson(this);
  
  /// 날짜를 DateTime으로 변환
  DateTime get dateTime => DateTime.parse(date);
  
  /// 가격을 포맷팅된 문자열로 반환 (예: "18,500원")
  String get formattedPrice => '${price.toStringAsFixed(0).replaceAllMapped(
    RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
    (Match m) => '${m[1]},',
  )}원';
  
  /// 비율을 백분율 문자열로 반환 (예: "+15%", "-10%")
  String get formattedRatio {
    if (ratio == null) return '';
    final percentage = ((ratio! - 1) * 100).toStringAsFixed(0);
    return ratio! >= 1 ? '+$percentage%' : '$percentage%';
  }
  
  /// 단위 변환 계수
  /// Requirements: 12.3 - 가격 단위 변환
  static const Map<String, Map<String, double>> _conversionRates = {
    'kg': {
      'kg': 1.0,
      'piece': 0.5,  // 1kg = 약 2마리 (평균)
      'box': 0.1,    // 1kg = 약 0.1상자 (평균)
    },
    'piece': {
      'kg': 2.0,     // 1마리 = 약 0.5kg (평균)
      'piece': 1.0,
      'box': 0.2,    // 1마리 = 약 0.2상자 (평균)
    },
    'box': {
      'kg': 10.0,    // 1상자 = 약 10kg (평균)
      'piece': 5.0,  // 1상자 = 약 5마리 (평균)
      'box': 1.0,
    },
  };
  
  /// 단위 표시명 매핑
  static const Map<String, String> _unitDisplayNames = {
    'kg': 'kg',
    'piece': '마리',
    'box': '상자',
  };
  
  /// 지정된 단위로 가격 변환
  /// Requirements: 12.3 - 가격 단위 변환 적용
  double convertPrice(String targetUnit) {
    // 단위가 같으면 그대로 반환
    if (unit == targetUnit) return price;
    
    // 변환 계수 조회
    final fromRates = _conversionRates[unit];
    if (fromRates == null) return price;
    
    final rate = fromRates[targetUnit];
    if (rate == null) return price;
    
    // 가격 변환
    return price * rate;
  }
  
  /// 변환된 가격을 포맷팅된 문자열로 반환
  String getFormattedPrice(String targetUnit) {
    final convertedPrice = convertPrice(targetUnit);
    return '${convertedPrice.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]},',
    )}원';
  }
  
  /// 단위 표시명 반환
  String getUnitDisplayName(String unitValue) {
    return _unitDisplayNames[unitValue] ?? unitValue;
  }
}
