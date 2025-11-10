import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/recognition_result.dart';
import '../../infrastructure/api_client.dart';
import '../../infrastructure/image_picker_service.dart';

/// 이미지 인식 상태
class RecognitionState {
  final bool isLoading;
  final RecognitionResult? result;
  final String? error;
  final File? selectedImage;

  RecognitionState({
    this.isLoading = false,
    this.result,
    this.error,
    this.selectedImage,
  });

  RecognitionState copyWith({
    bool? isLoading,
    RecognitionResult? result,
    String? error,
    File? selectedImage,
  }) {
    return RecognitionState(
      isLoading: isLoading ?? this.isLoading,
      result: result ?? this.result,
      error: error ?? this.error,
      selectedImage: selectedImage ?? this.selectedImage,
    );
  }
}

/// 이미지 인식 Provider
/// 
/// 이미지 선택, 업로드, 인식 결과 관리를 담당합니다.
/// Requirements: 1.2, 1.3, 11.4
class RecognitionNotifier extends StateNotifier<RecognitionState> {
  final ApiClient _apiClient;
  final ImagePickerService _imagePickerService;

  RecognitionNotifier(this._apiClient, this._imagePickerService)
      : super(RecognitionState());

  /// 카메라로 사진 촬영 후 인식
  Future<void> recognizeFromCamera() async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final image = await _imagePickerService.pickFromCamera();
      if (image == null) {
        // 사용자가 취소한 경우
        state = state.copyWith(isLoading: false);
        return;
      }

      state = state.copyWith(selectedImage: image);
      await _uploadAndRecognize(image);
    } on ImagePickerException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.message,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '카메라 접근 중 오류가 발생했습니다',
      );
    }
  }

  /// 갤러리에서 이미지 선택 후 인식
  Future<void> recognizeFromGallery() async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final image = await _imagePickerService.pickFromGallery();
      if (image == null) {
        // 사용자가 취소한 경우
        state = state.copyWith(isLoading: false);
        return;
      }

      state = state.copyWith(selectedImage: image);
      await _uploadAndRecognize(image);
    } on ImagePickerException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.message,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '갤러리 접근 중 오류가 발생했습니다',
      );
    }
  }

  /// 이미지 업로드 및 인식 수행
  Future<void> _uploadAndRecognize(File image) async {
    try {
      // 이미지 크기 검증 (최대 5MB)
      final fileSize = await image.length();
      if (fileSize > 5 * 1024 * 1024) {
        throw Exception('이미지 크기가 너무 큽니다 (최대 5MB)');
      }

      // BFF에 이미지 업로드
      final response = await _apiClient.uploadFile(
        '/recognition',
        image,
        fieldName: 'image',
      );

      // 응답 파싱
      final result = RecognitionResult.fromJson(response.data);

      // 인식 결과가 없는 경우
      if (result.candidates.isEmpty) {
        state = state.copyWith(
          isLoading: false,
          error: '품목을 인식할 수 없습니다. 직접 검색해주세요',
        );
        return;
      }

      // 성공
      state = state.copyWith(
        isLoading: false,
        result: result,
        error: null,
      );
    } on ApiException catch (e) {
      String errorMessage;
      switch (e.type) {
        case ApiExceptionType.network:
          errorMessage = '네트워크 연결을 확인해주세요';
          break;
        case ApiExceptionType.badRequest:
          errorMessage = '품목을 인식할 수 없습니다. 직접 검색해주세요';
          break;
        case ApiExceptionType.server:
          errorMessage = '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요';
          break;
        default:
          errorMessage = '이미지 인식 중 오류가 발생했습니다';
      }

      state = state.copyWith(
        isLoading: false,
        error: errorMessage,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: '이미지 인식 중 오류가 발생했습니다',
      );
    }
  }

  /// 상태 초기화
  void reset() {
    state = RecognitionState();
  }

  /// 에러 메시지 클리어
  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// RecognitionProvider 인스턴스
final recognitionProvider =
    StateNotifierProvider<RecognitionNotifier, RecognitionState>((ref) {
  final apiClient = ApiClient(); // .env 파일에서 API_BASE_URL 자동 로드
  final imagePickerService = ImagePickerService();
  return RecognitionNotifier(apiClient, imagePickerService);
});
