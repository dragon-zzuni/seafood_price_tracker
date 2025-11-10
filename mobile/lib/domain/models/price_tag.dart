import 'package:json_annotation/json_annotation.dart';
import 'package:flutter/material.dart';

/// 가격 태그 열거형
/// Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
enum PriceTag {
  @JsonValue('높음')
  high('높음'),
  
  @JsonValue('보통')
  normal('보통'),
  
  @JsonValue('낮음')
  low('낮음');
  
  const PriceTag(this.displayName);
  
  final String displayName;
  
  /// 태그에 따른 색상 반환
  Color get color {
    switch (this) {
      case PriceTag.high:
        return Colors.red;
      case PriceTag.normal:
        return Colors.grey;
      case PriceTag.low:
        return Colors.blue;
    }
  }
  
  /// 태그에 따른 배경 색상 반환 (연한 색상)
  Color get backgroundColor {
    switch (this) {
      case PriceTag.high:
        return Colors.red.withOpacity(0.1);
      case PriceTag.normal:
        return Colors.grey.withOpacity(0.1);
      case PriceTag.low:
        return Colors.blue.withOpacity(0.1);
    }
  }
}
