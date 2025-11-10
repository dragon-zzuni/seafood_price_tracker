import 'package:flutter/material.dart';
import '../../domain/models/item_detail.dart';

/// 품목 기본 정보 위젯
/// 
/// 품목명(한글/영문), 산지 정보, 제철/비성수기 배지를 표시합니다.
/// Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
class ItemInfoCard extends StatelessWidget {
  final ItemDetail item;
  final bool isInSeason;
  
  const ItemInfoCard({
    Key? key,
    required this.item,
    required this.isInSeason,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 품목명 및 제철 배지
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 품목명 (한글/영문)
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 한글명
                      Text(
                        item.nameKo,
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      // 영문명
                      if (item.nameEn != null && item.nameEn!.isNotEmpty)
                        Text(
                          item.nameEn!,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.grey[600],
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                // 제철/비성수기 배지
                _buildSeasonBadge(context),
              ],
            ),
            
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 12),
            
            // 산지 정보
            _buildInfoRow(
              context,
              icon: Icons.location_on_outlined,
              label: '주요 산지',
              value: item.defaultOrigin ?? '정보 없음',
            ),
            
            const SizedBox(height: 8),
            
            // 제철 기간
            _buildInfoRow(
              context,
              icon: Icons.calendar_today_outlined,
              label: '제철 기간',
              value: _getSeasonPeriodText(),
            ),
            
            const SizedBox(height: 8),
            
            // 카테고리
            _buildInfoRow(
              context,
              icon: Icons.category_outlined,
              label: '분류',
              value: _getCategoryText(item.category),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 제철/비성수기 배지 위젯
  Widget _buildSeasonBadge(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isInSeason ? Colors.green[50] : Colors.grey[200],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isInSeason ? Colors.green : Colors.grey,
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isInSeason ? Icons.check_circle : Icons.info_outline,
            size: 16,
            color: isInSeason ? Colors.green[700] : Colors.grey[700],
          ),
          const SizedBox(width: 4),
          Text(
            isInSeason ? '제철' : '비성수기',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isInSeason ? Colors.green[700] : Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
  
  /// 정보 행 위젯
  Widget _buildInfoRow(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          icon,
          size: 20,
          color: Colors.grey[600],
        ),
        const SizedBox(width: 8),
        Text(
          '$label: ',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[700],
            fontWeight: FontWeight.w500,
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
  
  /// 제철 기간 텍스트 생성
  String _getSeasonPeriodText() {
    if (item.season == null) {
      return '정보 없음';
    }
    
    final start = item.season!.from;
    final end = item.season!.to;
    
    if (start == end) {
      return '${start}월';
    } else if (start < end) {
      return '${start}월 ~ ${end}월';
    } else {
      // 연말-연초를 걸치는 경우 (예: 11월 ~ 2월)
      return '${start}월 ~ 다음해 ${end}월';
    }
  }
  
  /// 카테고리 한글 변환
  String _getCategoryText(String category) {
    switch (category.toLowerCase()) {
      case 'fish':
        return '생선';
      case 'shellfish':
        return '조개류';
      case 'crustacean':
        return '갑각류';
      case 'mollusk':
        return '연체동물';
      case 'seaweed':
        return '해조류';
      default:
        return '기타';
    }
  }
}
