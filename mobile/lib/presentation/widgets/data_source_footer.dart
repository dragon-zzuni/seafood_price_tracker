import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

/// 데이터 출처 표시 위젯
/// 
/// 화면 하단에 출처 정보와 수집 날짜를 표시합니다.
/// Requirements: 10.1, 10.2, 10.3, 10.4
class DataSourceFooter extends StatelessWidget {
  final List<String> dataSources;
  final DateTime? lastUpdated;
  
  const DataSourceFooter({
    Key? key,
    required this.dataSources,
    this.lastUpdated,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        border: Border(
          top: BorderSide(
            color: Colors.grey[300]!,
            width: 1,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // 출처 정보
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.info_outline,
                size: 14,
                color: Colors.grey[600],
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '데이터 출처',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: Colors.grey[700],
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _formatDataSources(),
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          // 수집 날짜 (있는 경우)
          if (lastUpdated != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  Icons.update,
                  size: 14,
                  color: Colors.grey[600],
                ),
                const SizedBox(width: 6),
                Text(
                  '최종 수집: ${_formatLastUpdated()}',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ],
          
          // 안내 문구
          const SizedBox(height: 8),
          Text(
            '※ 표시된 가격은 참고용이며, 실제 거래 가격과 다를 수 있습니다.',
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[500],
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }
  
  /// 데이터 출처를 쉼표로 구분하여 포맷팅
  String _formatDataSources() {
    if (dataSources.isEmpty) {
      return '정보 없음';
    }
    
    // 중복 제거 및 정렬
    final uniqueSources = dataSources.toSet().toList()..sort();
    
    // 쉼표로 구분하여 나열
    return uniqueSources.join(', ');
  }
  
  /// 최종 수집 날짜 포맷팅
  String _formatLastUpdated() {
    if (lastUpdated == null) return '';
    
    final now = DateTime.now();
    final difference = now.difference(lastUpdated!);
    
    // 오늘인 경우
    if (difference.inDays == 0) {
      if (difference.inHours == 0) {
        if (difference.inMinutes == 0) {
          return '방금 전';
        }
        return '${difference.inMinutes}분 전';
      }
      return '${difference.inHours}시간 전';
    }
    
    // 어제인 경우
    if (difference.inDays == 1) {
      return '어제';
    }
    
    // 일주일 이내인 경우
    if (difference.inDays < 7) {
      return '${difference.inDays}일 전';
    }
    
    // 그 외의 경우 날짜 표시
    return DateFormat('yyyy년 M월 d일').format(lastUpdated!);
  }
}
