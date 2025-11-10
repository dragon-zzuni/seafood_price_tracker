# 환경 변수 설정 가이드

## 🎯 핵심 요약

### .env 파일 없이도 실행 가능합니다!
앱은 기본 설정으로 실행되며, 백엔드 없이도 UI 테스트가 가능합니다.

## 📱 모바일 앱만 실행하기 (백엔드 없이)

```bash
cd mobile
flutter pub get
flutter run
```

**결과**: 
- ✅ 앱 UI는 정상 작동
- ⚠️ API 호출은 실패 (네트워크 오류 표시)
- 🎨 로딩, 에러 처리, 빈 상태 등 모든 UI 컴포넌트 확인 가능

## 🔧 환경 변수 설정 (선택사항)

### 방법 1: 모바일 앱만 설정 (권장)

`mobile/.env` 파일 하나만 생성:

```bash
# Android 에뮬레이터
API_BASE_URL=http://10.0.2.2:3000

# iOS 시뮬레이터
# API_BASE_URL=http://localhost:3000

# 실제 디바이스 (PC IP로 변경)
# API_BASE_URL=http://192.168.1.100:3000
```

### 방법 2: 전체 시스템 설정

#### 1️⃣ 루트 `.env` (Docker Compose용)
```bash
POSTGRES_DB=seafood
POSTGRES_USER=seafood_user
POSTGRES_PASSWORD=your_password

REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://seafood_user:your_password@postgres:5432/seafood

CORE_SERVICE_URL=http://core:8000
ML_SERVICE_URL=http://ml:8001

SCHEDULE_TIMES=08:30,11:30,15:30
PUBLIC_API_KEY=your_kamis_api_key
```

#### 2️⃣ `bff/.env`
```bash
REDIS_URL=redis://localhost:6379
CORE_SERVICE_URL=http://localhost:8000
ML_SERVICE_URL=http://localhost:8001
PORT=3000
```

#### 3️⃣ `core-service/.env`
```bash
DATABASE_URL=postgresql://seafood_user:your_password@localhost:5432/seafood
REDIS_URL=redis://localhost:6379
```

#### 4️⃣ `ml-service/.env`
```bash
MODEL_PATH=./models
DETECTION_MODEL=yolo_detect.pt
CLASSIFICATION_MODEL=yolo_classify.pt
```

#### 5️⃣ `mobile/.env`
```bash
API_BASE_URL=http://10.0.2.2:3000
```

## 🚀 실행 시나리오

### 시나리오 1: UI만 테스트 (백엔드 없음)
```bash
cd mobile
flutter run
```
- 모든 화면 탐색 가능
- 로딩/에러 상태 확인 가능
- 실제 데이터는 표시 안됨

### 시나리오 2: 백엔드 포함 전체 테스트
```bash
# 1. 백엔드 시작
docker-compose up -d

# 2. 모바일 앱 실행
cd mobile
flutter run
```
- 모든 기능 정상 작동
- 실제 데이터 조회 가능
- 이미지 인식 기능 사용 가능

### 시나리오 3: 개발 모드 (로컬 백엔드)
```bash
# 각 서비스를 개별 실행
# Terminal 1: Core Service
cd core-service
uvicorn app.main:app --reload --port 8000

# Terminal 2: BFF
cd bff
npm run start:dev

# Terminal 3: ML Service (선택)
cd ml-service
uvicorn app.main:app --reload --port 8001

# Terminal 4: Mobile
cd mobile
flutter run
```

## 🔍 환경 변수 우선순위

1. **mobile/.env** → 모바일 앱 설정
2. **코드 기본값** → `http://10.0.2.2:3000` (Android 에뮬레이터)
3. **환경 변수 없음** → 앱은 실행되지만 API 호출 실패

## ❓ FAQ

### Q: .env 파일이 없으면 앱이 실행 안되나요?
**A**: 아니요! 앱은 정상 실행되며 기본 URL을 사용합니다.

### Q: 백엔드 없이 테스트할 수 있나요?
**A**: 네! UI, 네비게이션, 에러 처리 등 모든 화면을 확인할 수 있습니다.

### Q: 환경 변수를 하나로 통합할 수 없나요?
**A**: 각 서비스가 독립적으로 실행되므로 개별 .env가 필요합니다. 하지만 **모바일 앱만 테스트**한다면 `mobile/.env` 하나면 충분합니다.

### Q: Docker Compose 사용 시 .env는 어디에?
**A**: 루트 디렉토리의 `.env` 파일 하나로 모든 서비스 설정이 가능합니다.

### Q: 실제 디바이스에서 테스트하려면?
**A**: 
1. PC의 로컬 IP 확인 (Windows: `ipconfig`, Mac: `ifconfig`)
2. `mobile/.env`에서 `API_BASE_URL=http://YOUR_PC_IP:3000` 설정
3. PC와 디바이스가 같은 Wi-Fi에 연결되어 있어야 함

## 🎯 권장 설정

### 개발 초기 (UI 개발)
```bash
# .env 파일 없이 실행
cd mobile
flutter run
```

### 기능 테스트
```bash
# mobile/.env만 생성
echo "API_BASE_URL=http://10.0.2.2:3000" > mobile/.env

# 백엔드 시작
docker-compose up -d

# 앱 실행
cd mobile
flutter run
```

### 프로덕션 배포
- 모든 .env 파일 설정
- 실제 도메인 사용
- 보안 강화 (HTTPS, 인증 등)
