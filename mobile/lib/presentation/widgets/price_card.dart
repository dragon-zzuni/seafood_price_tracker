import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../domain/models/market_price.dart';
import '../../application/providers/settings_provider.dart';

/// 가격 카드 위젯
/// 
/// 시장별 가격, 가격 태그 배지(높음/보통/낮음), 단위, 날짜를 표시합니다.
/// 사용자 설정에 따라 가격 단위를 변환하여 표시합니다.
/// Requirements: 4.1, 4.2, 4.5, 6.5, 6.6, 12.3
class PriceCard extends ConsumerWidget {
  final MarketPrice marketPrice;
  
  const PriceCard({
    Key? key,
    required this.marketPrice,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 사용자 설정에서 가격 단위 가져오기
    final priceUnit = ref.watch(priceUnitProvider);
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 시장명 및 가격 태그
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // 시장명
                Text(
                  marketPrice.market,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                // 가격 태그 배지
                _buildPriceTagBadge(context),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // 가격 및 단위 (설정된 단위로 변환하여 표시)
            // Requirements: 12.3 - 가격 단위 변환 적용
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      marketPrice.getFormattedPrice(priceUnit.value),
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: marketPrice.tag.color,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Padding(
                      padding: const EdgeInsets.only(bottom: 2),
                      child: Text(
                        '/ ${marketPrice.getUnitDisplayName(priceUnit.value)}',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[600],
                        ),
                      ),
                    ),
                  ],
                ),
                // 원본 단위가 다른 경우 원본 가격 표시
                if (marketPrice.unit != priceUnit.value)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      '원본: ${marketPrice.formattedPrice} / ${marketPrice.getUnitDisplayName(marketPrice.unit)}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                      ),
                    ),
                  ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // 기준 가격 대비 비율 (있는 경우)
            if (marketPrice.ratio != null && marketPrice.basePrice != null)
              _buildRatioInfo(context),
            
            const SizedBox(height: 8),
            const Divider(),
            const SizedBox(height: 8),
            
            // 하단 정보 (날짜, 산지)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // 수집 날짜
                Row(
                  children: [
                    Icon(
                      Icons.calendar_today,
                      size: 14,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(width: 4),
                    Text(
                      _formatDate(marketPrice.dateTime),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
                // 산지 (있는 경우)
                if (marketPrice.origin != null && marketPrice.origin!.isNotEmpty)
                  Row(
                    children: [
                      Icon(
                        Icons.location_on,
                        size: 14,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        marketPrice.origin!,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  /// 가격 태그 배지 위젯
  Widget _buildPriceTagBadge(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: marketPrice.tag.backgroundColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: marketPrice.tag.color,
          width: 1.5,
        ),
      ),
      child: Text(
        marketPrice.tag.displayName,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: marketPrice.tag.color,
        ),
      ),
    );
  }
  
  /// 기준 가격 대비 비율 정보 위젯
  Widget _buildRatioInfo(BuildContext context) {
    final isHigher = marketPrice.ratio! >= 1;
    final icon = isHigher ? Icons.arrow_upward : Icons.arrow_downward;
    final color = isHigher ? Colors.red : Colors.blue;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 16,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            '평균 대비 ${marketPrice.formattedRatio}',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            '(기준: ${_formatBasePrice()})',
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
  
  /// 날짜 포맷팅 (예: "2025년 11월 10일")
  String _formatDate(DateTime date) {
    return DateFormat('yyyy년 M월 d일').format(date);
  }
  
  /// 기준 가격 포맷팅
  String _formatBasePrice() {
    if (marketPrice.basePrice == null) return '';
    return '${marketPrice.basePrice!.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]},',
    )}원';
  }
}
