import 'dart:io';
import 'package:image_picker/image_picker.dart';

/// 이미지 선택 서비스
/// 카메라 촬영 및 갤러리에서 이미지 선택 기능 제공
class ImagePickerService {
  final ImagePicker _picker = ImagePicker();

  /// 카메라로 사진 촬영
  Future<File?> pickFromCamera() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image != null) {
        return File(image.path);
      }
      return null;
    } catch (e) {
      throw ImagePickerException('카메라 접근 중 오류가 발생했습니다: $e');
    }
  }

  /// 갤러리에서 이미지 선택
  Future<File?> pickFromGallery() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image != null) {
        return File(image.path);
      }
      return null;
    } catch (e) {
      throw ImagePickerException('갤러리 접근 중 오류가 발생했습니다: $e');
    }
  }

  /// 이미지 선택 소스 선택 다이얼로그 표시
  /// 사용자가 카메라 또는 갤러리를 선택할 수 있도록 함
  Future<File?> pickImage({required ImageSource source}) async {
    if (source == ImageSource.camera) {
      return pickFromCamera();
    } else {
      return pickFromGallery();
    }
  }
}

/// 이미지 선택 관련 예외
class ImagePickerException implements Exception {
  final String message;
  ImagePickerException(this.message);

  @override
  String toString() => message;
}
