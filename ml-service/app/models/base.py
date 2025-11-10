"""
모델 인터페이스 정의 (Strategy 패턴)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class BoundingBox:
    """Detection 결과 바운딩 박스"""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int = 0  # 수산물 클래스 ID


@dataclass
class ClassificationResult:
    """Classification 결과"""
    item_id: int
    item_name: str
    confidence: float


class DetectionModel(ABC):
    """
    객체 탐지 모델 인터페이스
    Strategy 패턴으로 다양한 Detection 모델을 교체 가능하게 설계
    """
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[BoundingBox]:
        """
        이미지에서 수산물 영역을 탐지
        
        Args:
            image: RGB 이미지 배열 (H, W, 3)
            
        Returns:
            탐지된 바운딩 박스 리스트
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """
        모델 파일 로딩
        
        Args:
            model_path: 모델 파일 경로
        """
        pass


class ClassificationModel(ABC):
    """
    품목 분류 모델 인터페이스
    Strategy 패턴으로 다양한 Classification 모델을 교체 가능하게 설계
    """
    
    @abstractmethod
    def classify(self, image: np.ndarray) -> List[ClassificationResult]:
        """
        이미지에서 품목을 분류
        
        Args:
            image: RGB 이미지 배열 (H, W, 3)
            
        Returns:
            분류 결과 리스트 (신뢰도 순으로 정렬)
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """
        모델 파일 로딩
        
        Args:
            model_path: 모델 파일 경로
        """
        pass
