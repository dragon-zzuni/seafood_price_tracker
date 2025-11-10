import 'package:json_annotation/json_annotation.dart';
import 'season_period.dart';

part 'item_detail.g.dart';

/// 품목 상세 정보 모델
/// Requirements: 3.1, 3.2, 3.3
@JsonSerializable()
class ItemDetail {
  /// 품목 ID
  final int id;
  
  /// 한글명
  @JsonKey(name: 'name_ko')
  final String nameKo;
  
  /// 영문명
  @JsonKey(name: 'name_en')
  final String? nameEn;
  
  /// 카테고리 (fish, shellfish, crustacean, etc)
  final String category;
  
  /// 제철 기간
  final SeasonPeriod? season;
  
  /// 기본 산지
  @JsonKey(name: 'default_origin')
  final String? defaultOrigin;
  
  /// 기본 단위
  @JsonKey(name: 'unit_default')
  final String? unitDefault;
  
  ItemDetail({
    required this.id,
    required this.nameKo,
    this.nameEn,
    required this.category,
    this.season,
    this.defaultOrigin,
    this.unitDefault,
  });
  
  factory ItemDetail.fromJson(Map<String, dynamic> json) => 
      _$ItemDetailFromJson(json);
  
  Map<String, dynamic> toJson() => _$ItemDetailToJson(this);
  
  /// 현재가 제철인지 확인
  bool get isInSeason => season?.isInSeason() ?? false;
  
  /// 제철 배지 텍스트
  String get seasonBadge => isInSeason ? '제철' : '비성수기';
}
