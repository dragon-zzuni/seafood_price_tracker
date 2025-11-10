import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../domain/models/settings.dart';
import '../../infrastructure/services/settings_service.dart';

/// SharedPreferences Provider
final sharedPreferencesProvider = FutureProvider<SharedPreferences>((ref) async {
  return await SharedPreferences.getInstance();
});

/// SettingsService Provider
final settingsServiceProvider = Provider<SettingsService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider).value;
  if (prefs == null) {
    throw Exception('SharedPreferences not initialized');
  }
  return SettingsService(prefs);
});

/// 사용자 설정 Provider
/// Requirements: 12.4, 12.5
final settingsProvider =
    StateNotifierProvider<SettingsNotifier, AsyncValue<UserSettings>>((ref) {
  final service = ref.watch(settingsServiceProvider);
  return SettingsNotifier(service);
});

/// 설정 상태 관리 Notifier
class SettingsNotifier extends StateNotifier<AsyncValue<UserSettings>> {
  final SettingsService _service;

  SettingsNotifier(this._service) : super(const AsyncValue.loading()) {
    _loadSettings();
  }

  /// 설정 로드
  Future<void> _loadSettings() async {
    state = const AsyncValue.loading();
    try {
      final settings = await _service.loadSettings();
      state = AsyncValue.data(settings);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// 시장 우선 표시 설정 업데이트
  Future<void> updateMarketPreference(MarketPreference preference) async {
    final currentSettings = state.value;
    if (currentSettings == null) return;

    // 낙관적 업데이트 (Optimistic Update)
    final updatedSettings = currentSettings.copyWith(
      marketPreference: preference,
    );
    state = AsyncValue.data(updatedSettings);

    try {
      await _service.updateMarketPreference(preference);
    } catch (e, stack) {
      // 실패 시 이전 상태로 롤백
      state = AsyncValue.data(currentSettings);
      state = AsyncValue.error(e, stack);
    }
  }

  /// 가격 단위 설정 업데이트
  Future<void> updatePriceUnit(PriceUnit unit) async {
    final currentSettings = state.value;
    if (currentSettings == null) return;

    // 낙관적 업데이트
    final updatedSettings = currentSettings.copyWith(
      priceUnit: unit,
    );
    state = AsyncValue.data(updatedSettings);

    try {
      await _service.updatePriceUnit(unit);
    } catch (e, stack) {
      // 실패 시 이전 상태로 롤백
      state = AsyncValue.data(currentSettings);
      state = AsyncValue.error(e, stack);
    }
  }

  /// 설정 초기화
  Future<void> resetSettings() async {
    try {
      await _service.resetSettings();
      state = const AsyncValue.data(UserSettings());
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// 설정 새로고침
  Future<void> refresh() async {
    await _loadSettings();
  }
}

/// 현재 시장 우선 표시 설정을 가져오는 Provider
final marketPreferenceProvider = Provider<MarketPreference>((ref) {
  final settings = ref.watch(settingsProvider).value;
  return settings?.marketPreference ?? MarketPreference.both;
});

/// 현재 가격 단위 설정을 가져오는 Provider
final priceUnitProvider = Provider<PriceUnit>((ref) {
  final settings = ref.watch(settingsProvider).value;
  return settings?.priceUnit ?? PriceUnit.kg;
});
