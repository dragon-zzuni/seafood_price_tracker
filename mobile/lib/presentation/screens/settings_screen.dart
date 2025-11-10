import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../application/providers/settings_provider.dart';
import '../../domain/models/settings.dart';

/// 사용자 설정 화면
/// Requirements: 12.1, 12.2, 12.3
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('설정'),
        elevation: 0,
      ),
      body: settingsAsync.when(
        data: (settings) => _buildSettingsContent(context, ref, settings),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('설정을 불러올 수 없습니다: $error'),
        ),
      ),
    );
  }

  Widget _buildSettingsContent(
    BuildContext context,
    WidgetRef ref,
    UserSettings settings,
  ) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildSectionTitle('시장 설정'),
        const SizedBox(height: 8),
        _buildMarketPreferenceCard(context, ref, settings),
        const SizedBox(height: 24),
        _buildSectionTitle('단위 설정'),
        const SizedBox(height: 8),
        _buildUnitPreferenceCard(context, ref, settings),
        const SizedBox(height: 24),
        _buildInfoCard(),
      ],
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: Colors.grey,
        ),
      ),
    );
  }

  /// 우선 표시 시장 선택 카드
  Widget _buildMarketPreferenceCard(
    BuildContext context,
    WidgetRef ref,
    UserSettings settings,
  ) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '우선 표시 시장',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              '대시보드에서 우선적으로 표시할 시장을 선택하세요',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 16),
            _buildMarketOption(
              context,
              ref,
              MarketPreference.garak,
              '가락시장 우선',
              '가락시장 가격을 먼저 표시합니다',
              settings.marketPreference,
            ),
            const Divider(height: 24),
            _buildMarketOption(
              context,
              ref,
              MarketPreference.noryangjin,
              '노량진 우선',
              '노량진수산시장 가격을 먼저 표시합니다',
              settings.marketPreference,
            ),
            const Divider(height: 24),
            _buildMarketOption(
              context,
              ref,
              MarketPreference.both,
              '둘 다 표시',
              '모든 시장 가격을 동등하게 표시합니다',
              settings.marketPreference,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMarketOption(
    BuildContext context,
    WidgetRef ref,
    MarketPreference preference,
    String title,
    String subtitle,
    MarketPreference currentPreference,
  ) {
    final isSelected = preference == currentPreference;

    return InkWell(
      onTap: () {
        ref.read(settingsProvider.notifier).updateMarketPreference(preference);
      },
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Radio<MarketPreference>(
              value: preference,
              groupValue: currentPreference,
              onChanged: (value) {
                if (value != null) {
                  ref
                      .read(settingsProvider.notifier)
                      .updateMarketPreference(value);
                }
              },
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 가격 단위 선택 카드
  Widget _buildUnitPreferenceCard(
    BuildContext context,
    WidgetRef ref,
    UserSettings settings,
  ) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '가격 단위',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              '가격 표시 시 우선적으로 사용할 단위를 선택하세요',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 16),
            _buildUnitOption(
              context,
              ref,
              PriceUnit.kg,
              'kg (킬로그램)',
              '무게 기준 가격',
              settings.priceUnit,
            ),
            const Divider(height: 24),
            _buildUnitOption(
              context,
              ref,
              PriceUnit.piece,
              '마리',
              '개체 수 기준 가격',
              settings.priceUnit,
            ),
            const Divider(height: 24),
            _buildUnitOption(
              context,
              ref,
              PriceUnit.box,
              '상자',
              '상자 단위 가격',
              settings.priceUnit,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUnitOption(
    BuildContext context,
    WidgetRef ref,
    PriceUnit unit,
    String title,
    String subtitle,
    PriceUnit currentUnit,
  ) {
    final isSelected = unit == currentUnit;

    return InkWell(
      onTap: () {
        ref.read(settingsProvider.notifier).updatePriceUnit(unit);
      },
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Radio<PriceUnit>(
              value: unit,
              groupValue: currentUnit,
              onChanged: (value) {
                if (value != null) {
                  ref.read(settingsProvider.notifier).updatePriceUnit(value);
                }
              },
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      elevation: 1,
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.info_outline, color: Colors.blue.shade700, size: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '설정은 자동으로 저장되며, 앱을 재시작해도 유지됩니다.',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.blue.shade900,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
