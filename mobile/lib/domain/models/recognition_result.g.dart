// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recognition_result.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

RecognitionResult _$RecognitionResultFromJson(Map<String, dynamic> json) =>
    RecognitionResult(
      candidates: (json['candidates'] as List<dynamic>)
          .map((e) => RecognitionCandidate.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$RecognitionResultToJson(RecognitionResult instance) =>
    <String, dynamic>{
      'candidates': instance.candidates,
    };

RecognitionCandidate _$RecognitionCandidateFromJson(
        Map<String, dynamic> json) =>
    RecognitionCandidate(
      itemId: (json['item_id'] as num).toInt(),
      itemName: json['item_name'] as String,
      confidence: (json['confidence'] as num).toDouble(),
    );

Map<String, dynamic> _$RecognitionCandidateToJson(
        RecognitionCandidate instance) =>
    <String, dynamic>{
      'item_id': instance.itemId,
      'item_name': instance.itemName,
      'confidence': instance.confidence,
    };
