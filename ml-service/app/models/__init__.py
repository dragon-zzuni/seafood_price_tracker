"""
모델 인터페이스 및 구현체
"""
from .base import DetectionModel, ClassificationModel, BoundingBox, ClassificationResult

# 모델 구현체는 필요할 때만 임포트 (대형 의존성)
# from .yolo_detector import YOLODetector
# from .clip_classifier import CLIPClassifier

__all__ = [
    'DetectionModel',
    'ClassificationModel',
    'BoundingBox',
    'ClassificationResult',
]
