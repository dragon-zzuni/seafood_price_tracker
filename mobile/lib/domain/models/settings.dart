/// 사용자 설정 모델
/// Requirements: 12.1, 12.2, 12.3, 12.4, 12.5

/// 시장 우선 표시 설정
enum MarketPreference {
  garak('garak', '가락시장'),
  noryangjin('noryangjin', '노량진'),
  both('both', '둘 다');

  const MarketPreference(this.value, this.displayName);
  final String value;
  final String displayName;

  static MarketPreference fromString(String value) {
    return MarketPreference.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MarketPreference.both,
    );
  }
}

/// 가격 단위 설정
enum PriceUnit {
  kg('kg', 'kg'),
  piece('piece', '마리'),
  box('box', '상자');

  const PriceUnit(this.value, this.displayName);
  final String value;
  final String displayName;

  static PriceUnit fromString(String value) {
    return PriceUnit.values.firstWhere(
      (e) => e.value == value,
      orElse: () => PriceUnit.kg,
    );
  }
}

/// 사용자 설정
class UserSettings {
  final MarketPreference marketPreference;
  final PriceUnit priceUnit;

  const UserSettings({
    this.marketPreference = MarketPreference.both,
    this.priceUnit = PriceUnit.kg,
  });

  UserSettings copyWith({
    MarketPreference? marketPreference,
    PriceUnit? priceUnit,
  }) {
    return UserSettings(
      marketPreference: marketPreference ?? this.marketPreference,
      priceUnit: priceUnit ?? this.priceUnit,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'marketPreference': marketPreference.value,
      'priceUnit': priceUnit.value,
    };
  }

  factory UserSettings.fromJson(Map<String, dynamic> json) {
    return UserSettings(
      marketPreference: MarketPreference.fromString(
        json['marketPreference'] as String? ?? 'both',
      ),
      priceUnit: PriceUnit.fromString(
        json['priceUnit'] as String? ?? 'kg',
      ),
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UserSettings &&
        other.marketPreference == marketPreference &&
        other.priceUnit == priceUnit;
  }

  @override
  int get hashCode => Object.hash(marketPreference, priceUnit);
}
