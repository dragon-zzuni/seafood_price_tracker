# ML Service - 이미지 인식 서비스

수산물 이미지를 분석하여 품목을 인식하는 머신러닝 서비스입니다.

## 기능

- **객체 탐지 (Detection)**: YOLO 모델을 사용하여 이미지에서 수산물 영역 탐지
- **품목 분류 (Classification)**: 탐지된 영역의 품목 분류
- **이미지 전처리**: 크기 검증, 리사이징, 정규화
- **파이프라인 통합**: Detection → Classification 자동 처리

## 아키텍처

```
app/
├── models/              # 모델 인터페이스 및 구현
│   ├── base.py         # 추상 클래스 (Strategy 패턴)
│   ├── yolo_detector.py
│   └── yolo_classifier.py
├── preprocessing/       # 이미지 전처리
│   └── image_processor.py
├── recognition/         # 인식 파이프라인
│   ├── pipeline.py
│   └── router.py       # API 엔드포인트
└── main.py             # FastAPI 앱
```

## 설치

```bash
pip install -r requirements.txt
```

## 환경 변수

`.env` 파일을 생성하고 다음 변수를 설정하세요:

```env
MODEL_PATH=/models
DETECTION_MODEL=yolo_detect.pt
CLASSIFICATION_MODEL=yolo_classify.pt
```

## 모델 파일

다음 YOLO 모델 파일이 필요합니다:

- `yolo_detect.pt`: 객체 탐지 모델
- `yolo_classify.pt`: 품목 분류 모델

모델 파일은 `MODEL_PATH`에 지정된 디렉토리에 배치하세요.

## 실행

### 로컬 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker 실행

```bash
docker build -t ml-service .
docker run -p 8001:8001 -v /path/to/models:/models ml-service
```

## API 사용법

### 이미지 인식

```bash
POST /recognition
Content-Type: multipart/form-data

# 예시
curl -X POST "http://localhost:8001/recognition" \
  -F "image=@flounder.jpg"
```

**응답:**

```json
{
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
```

### 헬스 체크

```bash
GET /recognition/health

# 응답
{
  "status": "healthy",
  "detector": "YOLODetector",
  "classifier": "YOLOClassifier",
  "confidence_threshold": 0.3,
  "max_results": 4
}
```

## 설정

### 신뢰도 임계값

`RecognitionPipeline` 생성 시 `confidence_threshold` 파라미터로 조정 가능 (기본값: 0.3)

### 최대 결과 수

`RecognitionPipeline` 생성 시 `max_results` 파라미터로 조정 가능 (기본값: 4)

### 이미지 크기 제한

`ImageProcessor` 생성 시 `max_size` 파라미터로 조정 가능 (기본값: 5MB)

## 모델 교체

Strategy 패턴을 사용하여 모델을 쉽게 교체할 수 있습니다:

```python
from app.models.base import DetectionModel, ClassificationModel

# 커스텀 Detection 모델
class CustomDetector(DetectionModel):
    def detect(self, image):
        # 구현
        pass
    
    def load_model(self, model_path):
        # 구현
        pass

# 파이프라인에 적용
pipeline = RecognitionPipeline(
    detector=CustomDetector("custom_model.pt"),
    classifier=YOLOClassifier("yolo_classify.pt")
)
```

## 에러 처리

- **400 Bad Request**: 이미지 크기 초과 또는 포맷 오류
- **500 Internal Server Error**: 모델 추론 실패
- **503 Service Unavailable**: ML 서비스 초기화 안 됨

## 로깅

로그는 표준 출력으로 출력됩니다:

```
2025-11-10 10:30:00 - app.recognition.pipeline - INFO - 이미지 인식 파이프라인 시작
2025-11-10 10:30:01 - app.recognition.pipeline - INFO - Detection 완료: 2개 영역 탐지
2025-11-10 10:30:02 - app.recognition.pipeline - INFO - 최종 결과: 3개 품목
```

## 성능

- **이미지 전처리**: ~50ms
- **Detection**: ~200ms (GPU 사용 시)
- **Classification**: ~100ms per box (GPU 사용 시)
- **전체 파이프라인**: ~500ms - 3s (이미지 및 탐지된 객체 수에 따라)

## 개발

### 테스트

```bash
pytest tests/
```

### 코드 스타일

```bash
black app/
flake8 app/
```

## 라이선스

MIT
