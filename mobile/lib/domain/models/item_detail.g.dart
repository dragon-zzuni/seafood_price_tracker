// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'item_detail.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ItemDetail _$ItemDetailFromJson(Map<String, dynamic> json) => ItemDetail(
      id: (json['id'] as num).toInt(),
      nameKo: json['name_ko'] as String,
      nameEn: json['name_en'] as String?,
      category: json['category'] as String,
      season: json['season'] == null
          ? null
          : SeasonPeriod.fromJson(json['season'] as Map<String, dynamic>),
      defaultOrigin: json['default_origin'] as String?,
      unitDefault: json['unit_default'] as String?,
    );

Map<String, dynamic> _$ItemDetailToJson(ItemDetail instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name_ko': instance.nameKo,
      'name_en': instance.nameEn,
      'category': instance.category,
      'season': instance.season,
      'default_origin': instance.defaultOrigin,
      'unit_default': instance.unitDefault,
    };
