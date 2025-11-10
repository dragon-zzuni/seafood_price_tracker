import 'package:flutter/material.dart';
import '../../infrastructure/services/error_handler.dart';

/// 에러 메시지를 표시하는 스낵바 유틸리티
class ErrorSnackbar {
  /// 에러 스낵바 표시 (3초 자동 숨김)
  static void show(
    BuildContext context,
    AppError error, {
    VoidCallback? onRetry,
  }) {
    final snackBar = SnackBar(
      content: _ErrorSnackbarContent(
        error: error,
        onRetry: onRetry,
      ),
      duration: const Duration(seconds: 3),
      behavior: SnackBarBehavior.floating,
      backgroundColor: _getBackgroundColor(error.type),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      margin: const EdgeInsets.all(16),
    );

    ScaffoldMessenger.of(context).showSnackBar(snackBar);
  }

  /// 간단한 메시지 스낵바 표시
  static void showMessage(
    BuildContext context,
    String message, {
    bool isError = true,
  }) {
    final snackBar = SnackBar(
      content: Text(message),
      duration: const Duration(seconds: 3),
      behavior: SnackBarBehavior.floating,
      backgroundColor: isError ? Colors.red[700] : Colors.green[700],
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      margin: const EdgeInsets.all(16),
    );

    ScaffoldMessenger.of(context).showSnackBar(snackBar);
  }

  static Color _getBackgroundColor(ErrorType type) {
    switch (type) {
      case ErrorType.network:
        return Colors.orange[700]!;
      case ErrorType.notFound:
        return Colors.blue[700]!;
      case ErrorType.recognition:
        return Colors.purple[700]!;
      case ErrorType.server:
      case ErrorType.timeout:
      case ErrorType.validation:
      case ErrorType.unknown:
        return Colors.red[700]!;
    }
  }
}

class _ErrorSnackbarContent extends StatelessWidget {
  final AppError error;
  final VoidCallback? onRetry;

  const _ErrorSnackbarContent({
    required this.error,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          _getIcon(error.type),
          color: Colors.white,
          size: 24,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                error.message,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (error.details != null) ...[
                const SizedBox(height: 4),
                Text(
                  error.details!,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
              ],
            ],
          ),
        ),
        if (error.canRetry && onRetry != null) ...[
          const SizedBox(width: 8),
          TextButton(
            onPressed: onRetry,
            style: TextButton.styleFrom(
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            ),
            child: const Text(
              '재시도',
              style: TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ],
    );
  }

  IconData _getIcon(ErrorType type) {
    switch (type) {
      case ErrorType.network:
        return Icons.wifi_off;
      case ErrorType.notFound:
        return Icons.search_off;
      case ErrorType.recognition:
        return Icons.image_not_supported;
      case ErrorType.timeout:
        return Icons.access_time;
      case ErrorType.validation:
        return Icons.error_outline;
      case ErrorType.server:
      case ErrorType.unknown:
        return Icons.error;
    }
  }
}
