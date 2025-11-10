import 'package:flutter/material.dart';

/// 데이터가 없을 때 표시하는 위젯
class EmptyStateWidget extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? message;
  final String? actionLabel;
  final VoidCallback? onAction;

  const EmptyStateWidget({
    super.key,
    required this.icon,
    required this.title,
    this.message,
    this.actionLabel,
    this.onAction,
  });

  /// 가격 데이터 없음
  factory EmptyStateWidget.noPrice({
    VoidCallback? onRefresh,
  }) {
    return EmptyStateWidget(
      icon: Icons.price_change_outlined,
      title: '가격 데이터가 없습니다',
      message: '최근 7일 이내의 가격 정보가 없습니다',
      actionLabel: onRefresh != null ? '새로고침' : null,
      onAction: onRefresh,
    );
  }

  /// 검색 결과 없음
  factory EmptyStateWidget.noSearchResults({
    String? query,
  }) {
    return EmptyStateWidget(
      icon: Icons.search_off,
      title: '검색 결과가 없습니다',
      message: query != null ? '"$query"에 대한 품목을 찾을 수 없습니다' : null,
    );
  }

  /// 인식 실패
  factory EmptyStateWidget.recognitionFailed({
    VoidCallback? onSearchManually,
  }) {
    return EmptyStateWidget(
      icon: Icons.image_not_supported,
      title: '품목을 인식할 수 없습니다',
      message: '사진이 흐리거나 품목이 명확하지 않습니다',
      actionLabel: '직접 검색하기',
      onAction: onSearchManually,
    );
  }

  /// 차트 데이터 부족
  factory EmptyStateWidget.insufficientChartData() {
    return const EmptyStateWidget(
      icon: Icons.show_chart,
      title: '데이터가 부족합니다',
      message: '차트를 표시하기 위한 데이터가 충분하지 않습니다',
    );
  }

  /// 네트워크 오류
  factory EmptyStateWidget.networkError({
    VoidCallback? onRetry,
  }) {
    return EmptyStateWidget(
      icon: Icons.wifi_off,
      title: '네트워크 연결을 확인해주세요',
      message: '인터넷 연결이 불안정합니다',
      actionLabel: '재시도',
      onAction: onRetry,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
              textAlign: TextAlign.center,
            ),
            if (message != null) ...[
              const SizedBox(height: 12),
              Text(
                message!,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
            ],
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onAction,
                icon: const Icon(Icons.refresh),
                label: Text(actionLabel!),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
