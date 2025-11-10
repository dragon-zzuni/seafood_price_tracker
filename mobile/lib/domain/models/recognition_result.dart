import 'package:json_annotation/json_annotation.dart';

part 'recognition_result.g.dart';

/// 이미지 인식 결과 모델
/// Requirements: 1.6, 1.7
@JsonSerializable()
class RecognitionResult {
  /// 인식된 품목 후보 리스트 (최대 4개)
  final List<RecognitionCandidate> candidates;
  
  RecognitionResult({
    required this.candidates,
  });
  
  factory RecognitionResult.fromJson(Map<String, dynamic> json) => 
      _$RecognitionResultFromJson(json);
  
  Map<String, dynamic> toJson() => _$RecognitionResultToJson(this);
  
  /// 인식 성공 여부 (최소 1개 이상의 후보가 있는지)
  bool get isSuccess => candidates.isNotEmpty;
  
  /// 가장 높은 신뢰도의 후보
  RecognitionCandidate? get topCandidate => 
      candidates.isNotEmpty ? candidates.first : null;
}

/// 인식 후보 품목
@JsonSerializable()
class RecognitionCandidate {
  /// 품목 ID
  @JsonKey(name: 'item_id')
  final int itemId;
  
  /// 품목명 (한글)
  @JsonKey(name: 'item_name')
  final String itemName;
  
  /// 신뢰도 점수 (0.0 ~ 1.0)
  final double confidence;
  
  RecognitionCandidate({
    required this.itemId,
    required this.itemName,
    required this.confidence,
  });
  
  factory RecognitionCandidate.fromJson(Map<String, dynamic> json) => 
      _$RecognitionCandidateFromJson(json);
  
  Map<String, dynamic> toJson() => _$RecognitionCandidateToJson(this);
  
  /// 신뢰도를 백분율 문자열로 반환 (예: "85%")
  String get confidencePercentage => '${(confidence * 100).toStringAsFixed(0)}%';
}
