import 'package:json_annotation/json_annotation.dart';

part 'item.g.dart';

@JsonSerializable()
class Item {
  final int id;
  @JsonKey(name: 'name_ko')
  final String nameKo;
  @JsonKey(name: 'name_en')
  final String? nameEn;
  final String category;
  
  Item({
    required this.id,
    required this.nameKo,
    this.nameEn,
    required this.category,
  });
  
  factory Item.fromJson(Map<String, dynamic> json) => _$ItemFromJson(json);
  Map<String, dynamic> toJson() => _$ItemToJson(this);
}
