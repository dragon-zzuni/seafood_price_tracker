"""
이미지 인식 파이프라인
Detection → Classification 통합
"""
from dataclasses import dataclass
from typing import List
import numpy as np
import logging

from ..models.base import DetectionModel, ClassificationModel, ClassificationResult
from ..preprocessing.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


@dataclass
class RecognitionResult:
    """
    최종 인식 결과
    """
    item_id: int
    item_name: str
    confidence: float


class RecognitionPipeline:
    """
    이미지 인식 파이프라인
    1. Detection: 수산물 영역 탐지
    2. Classification: 각 영역의 품목 분류
    3. 신뢰도 필터링 및 Top-4 반환
    """
    
    # 신뢰도 임계값
    CONFIDENCE_THRESHOLD = 0.3
    
    # 최대 반환 결과 수
    MAX_RESULTS = 4
    
    def __init__(
        self,
        detector: DetectionModel,
        classifier: ClassificationModel,
        image_processor: ImageProcessor = None,
        confidence_threshold: float = None,
        max_results: int = None
    ):
        """
        Args:
            detector: Detection 모델
            classifier: Classification 모델
            image_processor: 이미지 전처리기
            confidence_threshold: 신뢰도 임계값
            max_results: 최대 반환 결과 수
        """
        self.detector = detector
        self.classifier = classifier
        self.image_processor = image_processor or ImageProcessor()
        self.confidence_threshold = confidence_threshold or self.CONFIDENCE_THRESHOLD
        self.max_results = max_results or self.MAX_RESULTS
    
    def recognize(self, image: np.ndarray) -> List[RecognitionResult]:
        """
        이미지에서 수산물 인식
        
        Args:
            image: RGB 이미지 배열 (H, W, 3)
            
        Returns:
            인식 결과 리스트 (최대 max_results개, 신뢰도 순)
        """
        logger.info("이미지 인식 파이프라인 시작")
        
        # 1. Detection: 수산물 영역 탐지
        boxes = self.detector.detect(image)
        logger.info(f"Detection 완료: {len(boxes)}개 영역 탐지")
        
        if not boxes:
            logger.warning("탐지된 객체가 없습니다")
            return []
        
        # 2. Classification: 각 영역의 품목 분류
        all_results = []
        
        for i, box in enumerate(boxes):
            # 바운딩 박스 영역 크롭
            cropped = self.image_processor.crop_image(
                image, box.x1, box.y1, box.x2, box.y2
            )
            
            # 크롭된 영역이 너무 작으면 스킵
            if cropped.shape[0] < 10 or cropped.shape[1] < 10:
                logger.debug(f"Box {i}: 영역이 너무 작아 스킵")
                continue
            
            # 품목 분류
            classifications = self.classifier.classify(cropped)
            
            # Detection 신뢰도와 Classification 신뢰도를 결합
            for cls in classifications:
                combined_confidence = box.confidence * cls.confidence
                
                all_results.append(RecognitionResult(
                    item_id=cls.item_id,
                    item_name=cls.item_name,
                    confidence=combined_confidence
                ))
            
            logger.debug(f"Box {i}: {len(classifications)}개 분류 결과")
        
        # 3. 신뢰도 필터링
        filtered_results = [
            r for r in all_results 
            if r.confidence >= self.confidence_threshold
        ]
        
        logger.info(f"신뢰도 필터링: {len(all_results)} -> {len(filtered_results)}개")
        
        # 4. 중복 제거 (같은 품목은 가장 높은 신뢰도만 유지)
        unique_results = self._deduplicate_results(filtered_results)
        
        # 5. 신뢰도 순으로 정렬 및 Top-N 반환
        unique_results.sort(key=lambda r: r.confidence, reverse=True)
        final_results = unique_results[:self.max_results]
        
        logger.info(f"최종 결과: {len(final_results)}개 품목")
        for i, result in enumerate(final_results):
            logger.info(
                f"  {i+1}. {result.item_name} "
                f"(신뢰도: {result.confidence:.3f})"
            )
        
        return final_results
    
    def _deduplicate_results(
        self, 
        results: List[RecognitionResult]
    ) -> List[RecognitionResult]:
        """
        중복 품목 제거 (같은 품목은 가장 높은 신뢰도만 유지)
        
        Args:
            results: 인식 결과 리스트
            
        Returns:
            중복 제거된 결과 리스트
        """
        # 품목 ID별로 그룹화
        item_groups = {}
        for result in results:
            if result.item_id not in item_groups:
                item_groups[result.item_id] = []
            item_groups[result.item_id].append(result)
        
        # 각 그룹에서 가장 높은 신뢰도만 선택
        unique_results = []
        for item_id, group in item_groups.items():
            best_result = max(group, key=lambda r: r.confidence)
            unique_results.append(best_result)
        
        logger.debug(f"중복 제거: {len(results)} -> {len(unique_results)}개")
        
        return unique_results
