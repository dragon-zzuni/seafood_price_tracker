"""
이미지 인식 API 엔드포인트
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from .pipeline import RecognitionPipeline, RecognitionResult
from ..preprocessing.image_processor import ImageProcessor, ImageTooLargeException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recognition", tags=["recognition"])


class RecognitionResponse(BaseModel):
    """인식 결과 응답"""
    results: List[dict]
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "item_id": 0,
                        "item_name": "광어",
                        "confidence": 0.85
                    },
                    {
                        "item_id": 1,
                        "item_name": "고등어",
                        "confidence": 0.72
                    }
                ]
            }
        }


# 전역 파이프라인 인스턴스 (앱 시작 시 초기화됨)
_pipeline: RecognitionPipeline = None


def set_pipeline(pipeline: RecognitionPipeline):
    """파이프라인 설정"""
    global _pipeline
    _pipeline = pipeline


@router.post("/", response_model=RecognitionResponse)
async def recognize_image(
    image: UploadFile = File(..., description="이미지 파일 (최대 5MB)")
):
    """
    이미지에서 수산물 인식
    
    - **image**: 이미지 파일 (JPEG, PNG 등)
    
    Returns:
        인식된 품목 리스트 (최대 4개, 신뢰도 순)
    """
    if _pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="ML 서비스가 초기화되지 않았습니다"
        )
    
    try:
        # 이미지 읽기
        image_bytes = await image.read()
        logger.info(f"이미지 업로드: {image.filename}, {len(image_bytes)} bytes")
        
        # 이미지 전처리
        image_processor = ImageProcessor()
        image_array = image_processor.preprocess(image_bytes)
        
        # 인식 실행
        results = _pipeline.recognize(image_array)
        
        # 응답 포맷 변환
        response_results = [
            {
                "item_id": r.item_id,
                "item_name": r.item_name,
                "confidence": round(r.confidence, 3)
            }
            for r in results
        ]
        
        logger.info(f"인식 완료: {len(response_results)}개 품목")
        
        return RecognitionResponse(results=response_results)
        
    except ImageTooLargeException as e:
        logger.warning(f"이미지 크기 초과: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except ValueError as e:
        logger.warning(f"이미지 포맷 오류: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"이미지 포맷이 잘못되었습니다: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"인식 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="이미지 인식 중 오류가 발생했습니다"
        )


@router.get("/health")
async def health_check():
    """
    ML 서비스 상태 확인
    """
    if _pipeline is None:
        return {
            "status": "unhealthy",
            "message": "파이프라인이 초기화되지 않았습니다"
        }
    
    return {
        "status": "healthy",
        "detector": _pipeline.detector.__class__.__name__,
        "classifier": _pipeline.classifier.__class__.__name__,
        "confidence_threshold": _pipeline.confidence_threshold,
        "max_results": _pipeline.max_results
    }
