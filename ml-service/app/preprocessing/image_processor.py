"""
이미지 전처리 모듈
"""
from io import BytesIO
from typing import Tuple
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageTooLargeException(Exception):
    """이미지 크기가 너무 큰 경우 발생하는 예외"""
    pass


class ImageProcessor:
    """
    이미지 전처리 클래스
    - 크기 검증
    - 리사이징
    - 정규화
    """
    
    # 최대 이미지 크기 (5MB)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024
    
    # YOLO 입력 크기
    TARGET_SIZE = (640, 640)
    
    def __init__(self, max_size: int = None, target_size: Tuple[int, int] = None):
        """
        Args:
            max_size: 최대 이미지 크기 (바이트)
            target_size: 리사이징 목표 크기 (width, height)
        """
        self.max_size = max_size or self.MAX_IMAGE_SIZE
        self.target_size = target_size or self.TARGET_SIZE
    
    def validate_size(self, image_bytes: bytes) -> None:
        """
        이미지 크기 검증
        
        Args:
            image_bytes: 이미지 바이트 데이터
            
        Raises:
            ImageTooLargeException: 이미지가 최대 크기를 초과하는 경우
        """
        size = len(image_bytes)
        if size > self.max_size:
            raise ImageTooLargeException(
                f"이미지 크기가 너무 큽니다: {size / 1024 / 1024:.2f}MB "
                f"(최대: {self.max_size / 1024 / 1024:.2f}MB)"
            )
        logger.debug(f"이미지 크기 검증 통과: {size / 1024:.2f}KB")
    
    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        """
        이미지 전처리 파이프라인
        1. 크기 검증
        2. 이미지 로딩
        3. 리사이징
        4. 정규화
        
        Args:
            image_bytes: 이미지 바이트 데이터
            
        Returns:
            전처리된 이미지 배열 (H, W, 3), 값 범위 [0, 1]
            
        Raises:
            ImageTooLargeException: 이미지가 너무 큰 경우
            ValueError: 이미지 포맷이 잘못된 경우
        """
        # 1. 크기 검증
        self.validate_size(image_bytes)
        
        # 2. 이미지 로딩
        try:
            image = Image.open(BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"이미지 로딩 실패: {str(e)}")
        
        # RGB로 변환 (RGBA, Grayscale 등 처리)
        if image.mode != 'RGB':
            image = image.convert('RGB')
            logger.debug(f"이미지 모드 변환: {image.mode} -> RGB")
        
        # 3. 리사이징
        original_size = image.size
        image = self._resize_image(image)
        logger.debug(f"이미지 리사이징: {original_size} -> {image.size}")
        
        # 4. NumPy 배열로 변환 및 정규화
        image_array = np.array(image)
        image_array = self._normalize(image_array)
        
        logger.info(f"이미지 전처리 완료: shape={image_array.shape}, dtype={image_array.dtype}")
        return image_array
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        이미지 리사이징 (비율 유지하면서 패딩 추가)
        
        Args:
            image: PIL Image 객체
            
        Returns:
            리사이징된 이미지
        """
        # 비율 유지하면서 리사이징
        image.thumbnail(self.target_size, Image.Resampling.LANCZOS)
        
        # 정사각형으로 만들기 위해 패딩 추가
        new_image = Image.new('RGB', self.target_size, (114, 114, 114))  # 회색 패딩
        
        # 중앙에 배치
        paste_x = (self.target_size[0] - image.width) // 2
        paste_y = (self.target_size[1] - image.height) // 2
        new_image.paste(image, (paste_x, paste_y))
        
        return new_image
    
    def _normalize(self, image_array: np.ndarray) -> np.ndarray:
        """
        이미지 정규화 (0-255 -> 0-1)
        
        Args:
            image_array: 이미지 배열
            
        Returns:
            정규화된 이미지 배열
        """
        # YOLO는 0-255 범위를 사용하므로 정규화하지 않음
        # 다른 모델을 사용할 경우 여기서 정규화 수행
        return image_array
    
    def crop_image(self, image: np.ndarray, x1: float, y1: float, 
                   x2: float, y2: float) -> np.ndarray:
        """
        이미지에서 특정 영역 크롭
        
        Args:
            image: 원본 이미지 배열
            x1, y1, x2, y2: 바운딩 박스 좌표
            
        Returns:
            크롭된 이미지 배열
        """
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # 좌표 범위 검증
        h, w = image.shape[:2]
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        cropped = image[y1:y2, x1:x2]
        logger.debug(f"이미지 크롭: ({x1}, {y1}, {x2}, {y2}) -> shape={cropped.shape}")
        
        return cropped
