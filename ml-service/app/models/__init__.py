"""
모델 인터페이스 및 구현체
"""
from .base import DetectionModel, ClassificationModel, BoundingBox, ClassificationResult

# YOLO 모듈은 필요할 때만 임포트 (ultralytics 의존성)
# from .yolo_detector import YOLODetector
# from .yolo_classifier import YOLOClassifier

__all__ = [
    'DetectionModel',
    'ClassificationModel',
    'BoundingBox',
    'ClassificationResult',
]
