import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// API 통신을 위한 클라이언트 클래스
/// 
/// dio를 사용한 HTTP 요청 처리, 에러 핸들링, 재시도 로직을 제공합니다.
/// Requirements: 11.1, 11.3
class ApiClient {
  final Dio _dio;
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 1);
  
  ApiClient({String? baseUrl}) 
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl ?? dotenv.env['API_BASE_URL'] ?? 'http://10.0.2.2:3000/api',
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        )) {
    _setupInterceptors();
  }
  
  /// 인터셉터 설정 (로깅 및 에러 처리)
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          // 요청 로깅
          print('[API Request] ${options.method} ${options.path}');
          return handler.next(options);
        },
        onResponse: (response, handler) {
          // 응답 로깅
          print('[API Response] ${response.statusCode} ${response.requestOptions.path}');
          return handler.next(response);
        },
        onError: (error, handler) {
          // 에러 로깅
          print('[API Error] ${error.message}');
          return handler.next(error);
        },
      ),
    );
  }
  
  /// GET 요청 (재시도 로직 포함)
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    int retryCount = 0,
  }) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } on DioException catch (e) {
      return _handleError(e, () => get(path, queryParameters: queryParameters, retryCount: retryCount + 1), retryCount);
    }
  }
  
  /// POST 요청 (재시도 로직 포함)
  Future<Response> post(
    String path, {
    dynamic data,
    int retryCount = 0,
  }) async {
    try {
      return await _dio.post(path, data: data);
    } on DioException catch (e) {
      return _handleError(e, () => post(path, data: data, retryCount: retryCount + 1), retryCount);
    }
  }
  
  /// Multipart 파일 업로드 (이미지 인식용)
  Future<Response> uploadFile(
    String path,
    File file, {
    String fieldName = 'image',
    int retryCount = 0,
  }) async {
    try {
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(
          file.path,
          filename: file.path.split('/').last,
        ),
      });
      
      return await _dio.post(
        path,
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );
    } on DioException catch (e) {
      return _handleError(
        e,
        () => uploadFile(path, file, fieldName: fieldName, retryCount: retryCount + 1),
        retryCount,
      );
    }
  }
  
  /// 에러 핸들링 및 재시도 로직
  Future<Response> _handleError(
    DioException error,
    Future<Response> Function() retryFunction,
    int retryCount,
  ) async {
    // 재시도 가능한 에러인지 확인
    if (_shouldRetry(error) && retryCount < maxRetries) {
      print('[API Retry] Attempt ${retryCount + 1}/$maxRetries');
      await Future.delayed(retryDelay * (retryCount + 1)); // 지수 백오프
      return retryFunction();
    }
    
    // 재시도 불가능하거나 최대 재시도 횟수 초과
    throw _convertToAppException(error);
  }
  
  /// 재시도 가능 여부 판단
  bool _shouldRetry(DioException error) {
    // 네트워크 오류, 타임아웃, 5xx 서버 오류는 재시도
    return error.type == DioExceptionType.connectionTimeout ||
           error.type == DioExceptionType.receiveTimeout ||
           error.type == DioExceptionType.sendTimeout ||
           error.type == DioExceptionType.connectionError ||
           (error.response?.statusCode != null && 
            error.response!.statusCode! >= 500);
  }
  
  /// DioException을 앱 전용 예외로 변환
  ApiException _convertToAppException(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
      case DioExceptionType.sendTimeout:
        return ApiException(
          message: '네트워크 연결을 확인해주세요',
          type: ApiExceptionType.network,
          originalError: error,
        );
      
      case DioExceptionType.connectionError:
        return ApiException(
          message: '서버에 연결할 수 없습니다',
          type: ApiExceptionType.network,
          originalError: error,
        );
      
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        if (statusCode == 404) {
          return ApiException(
            message: '요청한 데이터를 찾을 수 없습니다',
            type: ApiExceptionType.notFound,
            originalError: error,
          );
        } else if (statusCode == 400) {
          return ApiException(
            message: '잘못된 요청입니다',
            type: ApiExceptionType.badRequest,
            originalError: error,
          );
        } else if (statusCode != null && statusCode >= 500) {
          return ApiException(
            message: '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요',
            type: ApiExceptionType.server,
            originalError: error,
          );
        }
        return ApiException(
          message: '알 수 없는 오류가 발생했습니다',
          type: ApiExceptionType.unknown,
          originalError: error,
        );
      
      default:
        return ApiException(
          message: '알 수 없는 오류가 발생했습니다',
          type: ApiExceptionType.unknown,
          originalError: error,
        );
    }
  }
}

/// API 예외 타입
enum ApiExceptionType {
  network,      // 네트워크 오류
  notFound,     // 404
  badRequest,   // 400
  server,       // 5xx
  unknown,      // 기타
}

/// API 예외 클래스
class ApiException implements Exception {
  final String message;
  final ApiExceptionType type;
  final DioException? originalError;
  
  ApiException({
    required this.message,
    required this.type,
    this.originalError,
  });
  
  @override
  String toString() => message;
}
