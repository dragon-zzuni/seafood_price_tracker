from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from .models.yolo_detector import YOLODetector
from .models.clip_classifier import CLIPClassifier
from .recognition.pipeline import RecognitionPipeline
from .recognition import router as recognition_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Seafood Price Tracker ML Service",
    description="이미지 인식 서비스 (Detection + Classification)",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    앱 시작 시 ML 모델 로딩 및 파이프라인 초기화
    """
    try:
        # 환경 변수에서 모델 경로 가져오기
        model_path = os.getenv("MODEL_PATH", "/models")
        detection_model = os.getenv("DETECTION_MODEL", "yolo12n.pt")
        clip_model_name = os.getenv(
            "CLIP_MODEL_NAME",
            CLIPClassifier.DEFAULT_MODEL_NAME,
        )
        clip_pretrained = os.getenv(
            "CLIP_PRETRAINED",
            CLIPClassifier.DEFAULT_PRETRAINED,
        )
        clip_device = os.getenv("CLIP_DEVICE") or None
        clip_prompt_template = os.getenv("CLIP_PROMPT_TEMPLATE")
        clip_labels_raw = os.getenv("CLIP_CLASS_LABELS")
        clip_labels = (
            [label.strip() for label in clip_labels_raw.split(",") if label.strip()]
            if clip_labels_raw
            else None
        )
        
        detection_path = os.path.join(model_path, detection_model)
        
        logger.info("ML 모델 로딩 시작...")
        
        # 모델 파일 존재 확인
        if not os.path.exists(detection_path):
            logger.warning(f"Detection 모델 파일이 없습니다: {detection_path}")
            logger.warning("데모 모드로 실행됩니다 (실제 모델 없이)")
            # 실제 배포 시에는 여기서 예외를 발생시켜야 함
            return
        
        # Detection 모델 로딩
        detector = YOLODetector(detection_path)
        
        # CLIP Classification 모델 로딩
        classifier = CLIPClassifier(
            model_name=clip_model_name,
            pretrained=clip_pretrained,
            device=clip_device,
            class_labels=clip_labels,
            prompt_template=clip_prompt_template,
        )
        
        # 파이프라인 생성
        pipeline = RecognitionPipeline(
            detector=detector,
            classifier=classifier
        )
        
        # 라우터에 파이프라인 설정
        recognition_router.set_pipeline(pipeline)
        
        logger.info("ML 모델 로딩 완료")
        
    except Exception as e:
        logger.error(f"ML 모델 로딩 실패: {str(e)}", exc_info=True)
        # 실제 배포 시에는 여기서 앱을 종료해야 함
        # raise


# 라우터 등록
app.include_router(recognition_router.router)


@app.get("/")
async def root():
    return {
        "message": "ML Service is running",
        "version": "1.0.0",
        "endpoints": {
            "recognition": "/recognition",
            "health": "/recognition/health"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
