import 'package:dio/dio.dart';

/// 에러 타입 정의
enum ErrorType {
  network,
  notFound,
  validation,
  recognition,
  server,
  timeout,
  unknown,
}

/// 사용자 친화적 에러 메시지를 제공하는 클래스
class AppError {
  final ErrorType type;
  final String message;
  final String? details;
  final bool canRetry;

  AppError({
    required this.type,
    required this.message,
    this.details,
    this.canRetry = false,
  });

  /// DioException을 AppError로 변환
  factory AppError.fromDioException(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return AppError(
        type: ErrorType.timeout,
        message: '요청 시간이 초과되었습니다. 다시 시도해주세요',
        canRetry: true,
      );
    }

    if (error.type == DioExceptionType.connectionError) {
      return AppError(
        type: ErrorType.network,
        message: '네트워크 연결을 확인해주세요',
        canRetry: true,
      );
    }

    if (error.response != null) {
      final statusCode = error.response!.statusCode;
      final data = error.response!.data;

      // BFF의 표준 에러 응답 처리
      if (data is Map<String, dynamic>) {
        final message = data['message'] as String?;
        final errorType = data['errorType'] as String?;

        if (statusCode == 404) {
          return AppError(
            type: ErrorType.notFound,
            message: message ?? '요청한 정보를 찾을 수 없습니다',
            canRetry: false,
          );
        }

        if (statusCode == 400 || statusCode == 422) {
          return AppError(
            type: ErrorType.validation,
            message: message ?? '입력 데이터가 올바르지 않습니다',
            canRetry: false,
          );
        }

        // 인식 실패 처리
        if (errorType == 'RecognitionFailedException') {
          return AppError(
            type: ErrorType.recognition,
            message: '품목을 인식할 수 없습니다. 직접 검색해주세요',
            canRetry: false,
          );
        }

        if (statusCode != null && statusCode >= 500) {
          return AppError(
            type: ErrorType.server,
            message: message ?? '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요',
            canRetry: true,
          );
        }

        // 기타 에러
        if (message != null) {
          return AppError(
            type: ErrorType.unknown,
            message: message,
            canRetry: statusCode != null && statusCode >= 500,
          );
        }
      }
    }

    return AppError(
      type: ErrorType.unknown,
      message: '알 수 없는 오류가 발생했습니다',
      canRetry: false,
    );
  }

  /// 일반 Exception을 AppError로 변환
  factory AppError.fromException(Exception error) {
    if (error is DioException) {
      return AppError.fromDioException(error);
    }

    return AppError(
      type: ErrorType.unknown,
      message: '오류가 발생했습니다: ${error.toString()}',
      canRetry: false,
    );
  }
}
