import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../../domain/models/settings.dart';

/// 설정 저장/로딩 서비스
/// Requirements: 12.4, 12.5
class SettingsService {
  static const String _settingsKey = 'user_settings';

  final SharedPreferences _prefs;

  SettingsService(this._prefs);

  /// 설정 로드
  Future<UserSettings> loadSettings() async {
    try {
      final jsonString = _prefs.getString(_settingsKey);
      if (jsonString == null) {
        // 기본 설정 반환
        return const UserSettings();
      }

      final json = jsonDecode(jsonString) as Map<String, dynamic>;
      return UserSettings.fromJson(json);
    } catch (e) {
      // 파싱 실패 시 기본 설정 반환
      return const UserSettings();
    }
  }

  /// 설정 저장
  Future<void> saveSettings(UserSettings settings) async {
    final jsonString = jsonEncode(settings.toJson());
    await _prefs.setString(_settingsKey, jsonString);
  }

  /// 시장 우선 표시 설정 업데이트
  Future<void> updateMarketPreference(MarketPreference preference) async {
    final currentSettings = await loadSettings();
    final updatedSettings = currentSettings.copyWith(
      marketPreference: preference,
    );
    await saveSettings(updatedSettings);
  }

  /// 가격 단위 설정 업데이트
  Future<void> updatePriceUnit(PriceUnit unit) async {
    final currentSettings = await loadSettings();
    final updatedSettings = currentSettings.copyWith(
      priceUnit: unit,
    );
    await saveSettings(updatedSettings);
  }

  /// 설정 초기화
  Future<void> resetSettings() async {
    await _prefs.remove(_settingsKey);
  }
}
