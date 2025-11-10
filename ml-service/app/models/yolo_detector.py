"""
YOLO 기반 객체 탐지 모듈
"""
from typing import List
import numpy as np
from ultralytics import YOLO
import logging

from .base import DetectionModel, BoundingBox

logger = logging.getLogger(__name__)


class YOLODetector(DetectionModel):
    """
    YOLO 모델을 사용한 수산물 객체 탐지
    """
    
    def __init__(self, model_path: str = None):
        """
        Args:
            model_path: YOLO 모델 파일 경로 (.pt 파일)
        """
        self.model = None
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> None:
        """
        YOLO 모델 로딩
        
        Args:
            model_path: 모델 파일 경로
        """
        try:
            self.model = YOLO(model_path)
            logger.info(f"YOLO Detection 모델 로딩 완료: {model_path}")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {str(e)}")
            raise
    
    def detect(self, image: np.ndarray) -> List[BoundingBox]:
        """
        이미지에서 수산물 영역 탐지
        
        Args:
            image: RGB 이미지 배열 (H, W, 3)
            
        Returns:
            탐지된 바운딩 박스 리스트
        """
        if self.model is None:
            raise RuntimeError("모델이 로딩되지 않았습니다. load_model()을 먼저 호출하세요.")
        
        try:
            # YOLO 추론 실행
            results = self.model(image, verbose=False)
            
            # 결과 파싱
            boxes = self._parse_results(results)
            
            logger.info(f"Detection 완료: {len(boxes)}개 객체 탐지")
            return boxes
            
        except Exception as e:
            logger.error(f"Detection 실패: {str(e)}")
            raise
    
    def _parse_results(self, results) -> List[BoundingBox]:
        """
        YOLO 결과를 BoundingBox 리스트로 변환
        
        Args:
            results: YOLO 추론 결과
            
        Returns:
            BoundingBox 리스트
        """
        boxes = []
        
        # YOLO 결과에서 박스 정보 추출
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue
                
            for box in result.boxes:
                # 좌표 추출 (xyxy 포맷)
                coords = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = coords
                
                # 신뢰도 추출
                confidence = float(box.conf[0].cpu().numpy())
                
                # 클래스 ID 추출
                class_id = int(box.cls[0].cpu().numpy())
                
                boxes.append(BoundingBox(
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                    confidence=confidence,
                    class_id=class_id
                ))
        
        # 신뢰도 순으로 정렬
        boxes.sort(key=lambda b: b.confidence, reverse=True)
        
        return boxes
