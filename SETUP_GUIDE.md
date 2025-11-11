# 수산물 가격 추적 앱 설정 가이드

## 1. Android v1 Embedding 오류 해결 ✅

MainActivity.kt 파일이 생성되었습니다. 이제 Flutter v2 embedding을 사용합니다.

## 2. 환경 변수 설정

프로젝트를 실행하기 전에 **루트 디렉토리의 `.env`** 파일만 준비하면 됩니다.  
모바일 앱 역시 루트 `.env`를 직접 로드하므로 별도의 `mobile/.env` 파일이 필요 없습니다.

### 2.1 루트 디렉토리 `.env`

```bash
# PostgreSQL
POSTGRES_DB=seafood
POSTGRES_USER=seafood_user
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://seafood_user:your_secure_password_here@postgres:5432/seafood

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379

# 서비스 URL (BFF가 사용)
CORE_SERVICE_URL=http://core:8000
ML_SERVICE_URL=http://ml:8001

# Data Ingestion
SCHEDULE_TIMES=08:30,11:30,15:30
RUN_IMMEDIATELY=false
GARAK_API_KEY=your_garak_api_key_here
PUBLIC_DATA_API_KEY=your_kamis_api_key_here

# ML Service
MODEL_PATH=/models
DETECTION_MODEL=yolo12n.pt
CLIP_MODEL_NAME=ViT-B-32
CLIP_PRETRAINED=openai
```

모바일 실행 시 루트 `.env`의 `API_BASE_URL` 값을 자동으로 사용합니다.  
Android/iOS/실제 디바이스 전환 시 루트 파일의 값을 수정하세요.

## 3. 빠른 시작 (개발 환경)

### 3.1 백엔드 서비스 시작 (Docker Compose)

```bash
# 루트 디렉토리에서
docker-compose up -d
```

이 명령어는 다음 서비스들을 시작합니다:
- PostgreSQL (포트 5432)
- Redis (포트 6379)
- Core Service (포트 8000)
- BFF (포트 3000)
- ML Service (포트 8001)
- Data Ingestion (스케줄러)

### 3.2 모바일 앱 실행

```bash
cd mobile

# 의존성 설치
flutter pub get

# Android 에뮬레이터 실행
flutter run
```

## 4. 환경별 설정

### 개발 환경 (로컬)
- `API_BASE_URL=http://10.0.2.2:3000` (Android 에뮬레이터)
- `API_BASE_URL=http://localhost:3000` (iOS 시뮬레이터)

### 실제 디바이스 테스트
- `API_BASE_URL=http://192.168.x.x:3000` (PC의 로컬 IP 주소)

### 프로덕션
- `API_BASE_URL=https://api.yourdomain.com`

## 5. 필수 API 키

### 공공데이터/API 키
1. https://www.kamis.or.kr 접속
2. 회원가입 및 로그인
3. API 신청
4. 발급받은 키를 `PUBLIC_DATA_API_KEY`에 설정
5. 가락시장 API 사용 시 `GARAK_API_KEY`도 함께 설정

## 6. 데이터베이스 초기화

```bash
# Core Service 컨테이너에서 마이그레이션 실행
docker-compose exec core alembic upgrade head
```

## 7. 문제 해결

### Android 빌드 오류
```bash
cd mobile/android
./gradlew clean
cd ../..
flutter clean
flutter pub get
flutter run
```

### 네트워크 연결 오류
- Android 에뮬레이터: `10.0.2.2`는 호스트 머신의 localhost를 가리킵니다
- 실제 디바이스: PC와 같은 Wi-Fi 네트워크에 연결되어 있는지 확인
- 방화벽: 포트 3000이 열려있는지 확인

### ML 모델 파일 없음
ML 서비스는 YOLO Detection 모델 파일이 필요합니다:
- `ml-service/models/yolo12n.pt` (또는 호환되는 YOLO 가중치)

분류는 OpenAI CLIP 기본 모델을 사용하므로 별도 학습 파일이 없어도 동작합니다.

## 8. 다음 단계

1. ✅ MainActivity.kt 생성 완료
2. 📝 환경 변수 파일 생성 (위 내용 참고)
3. 🐳 Docker Compose로 백엔드 시작
4. 📱 Flutter 앱 실행
5. 🧪 기능 테스트

## 9. 유용한 명령어

```bash
# 모든 서비스 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f bff

# 서비스 재시작
docker-compose restart bff

# 모든 서비스 중지
docker-compose down

# 데이터베이스 포함 모두 삭제
docker-compose down -v
```
