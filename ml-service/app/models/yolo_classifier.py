"""
YOLO 기반 품목 분류 모듈
"""
from typing import List, Dict
import numpy as np
from ultralytics import YOLO
import logging

from .base import ClassificationModel, ClassificationResult

logger = logging.getLogger(__name__)


class YOLOClassifier(ClassificationModel):
    """
    YOLO 모델을 사용한 수산물 품목 분류
    """
    
    # 품목 ID와 이름 매핑 (실제로는 DB나 설정 파일에서 로딩)
    ITEM_MAPPING: Dict[int, str] = {
        0: "광어",
        1: "고등어",
        2: "갈치",
        3: "조기",
        4: "오징어",
        5: "낙지",
        6: "문어",
        7: "새우",
        8: "꽃게",
        9: "대게",
        10: "전복",
        11: "굴",
        12: "바지락",
        13: "홍합",
        14: "멍게",
    }
    
    def __init__(self, model_path: str = None, item_mapping: Dict[int, str] = None):
        """
        Args:
            model_path: YOLO 모델 파일 경로 (.pt 파일)
            item_mapping: 품목 ID와 이름 매핑 (선택사항)
        """
        self.model = None
        if item_mapping:
            self.ITEM_MAPPING = item_mapping
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
            logger.info(f"YOLO Classification 모델 로딩 완료: {model_path}")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {str(e)}")
            raise
    
    def classify(self, image: np.ndarray) -> List[ClassificationResult]:
        """
        이미지에서 품목 분류
        
        Args:
            image: RGB 이미지 배열 (H, W, 3)
            
        Returns:
            분류 결과 리스트 (신뢰도 순으로 정렬)
        """
        if self.model is None:
            raise RuntimeError("모델이 로딩되지 않았습니다. load_model()을 먼저 호출하세요.")
        
        try:
            # YOLO 추론 실행
            results = self.model(image, verbose=False)
            
            # 결과 파싱
            classifications = self._parse_results(results)
            
            logger.info(f"Classification 완료: {len(classifications)}개 후보")
            return classifications
            
        except Exception as e:
            logger.error(f"Classification 실패: {str(e)}")
            raise
    
    def _parse_results(self, results) -> List[ClassificationResult]:
        """
        YOLO 결과를 ClassificationResult 리스트로 변환
        
        Args:
            results: YOLO 추론 결과
            
        Returns:
            ClassificationResult 리스트 (신뢰도 순으로 정렬)
        """
        classifications = []
        
        # YOLO 결과에서 분류 정보 추출
        for result in results:
            if result.probs is None:
                # Detection 모드인 경우 boxes에서 추출
                if result.boxes is not None and len(result.boxes) > 0:
                    for box in result.boxes:
                        class_id = int(box.cls[0].cpu().numpy())
                        confidence = float(box.conf[0].cpu().numpy())
                        
                        item_name = self.ITEM_MAPPING.get(class_id, f"Unknown_{class_id}")
                        
                        classifications.append(ClassificationResult(
                            item_id=class_id,
                            item_name=item_name,
                            confidence=confidence
                        ))
            else:
                # Classification 모드인 경우 probs에서 추출
                probs = result.probs.data.cpu().numpy()
                
                # 모든 클래스의 확률을 ClassificationResult로 변환
                for class_id, prob in enumerate(probs):
                    item_name = self.ITEM_MAPPING.get(class_id, f"Unknown_{class_id}")
                    
                    classifications.append(ClassificationResult(
                        item_id=class_id,
                        item_name=item_name,
                        confidence=float(prob)
                    ))
        
        # 신뢰도 순으로 정렬
        classifications.sort(key=lambda c: c.confidence, reverse=True)
        
        return classifications
