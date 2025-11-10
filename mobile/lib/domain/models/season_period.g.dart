// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'season_period.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SeasonPeriod _$SeasonPeriodFromJson(Map<String, dynamic> json) => SeasonPeriod(
      from: (json['from'] as num).toInt(),
      to: (json['to'] as num).toInt(),
    );

Map<String, dynamic> _$SeasonPeriodToJson(SeasonPeriod instance) =>
    <String, dynamic>{
      'from': instance.from,
      'to': instance.to,
    };
