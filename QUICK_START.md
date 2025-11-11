# 빠른 시작 가이드 🚀

## 문제 해결 완료 ✅

1. **Android v1 embedding 오류** → MainActivity.kt 생성 완료
2. **환경 변수 설정** → .env 파일 생성 및 설정 완료

## 지금 바로 실행하기

### 1단계: 의존성 설치

```bash
cd mobile
flutter pub get
```

### 2단계: 앱 실행

```bash
flutter run
```

## 현재 설정된 환경 변수

### 루트 `.env`
```
API_BASE_URL=http://10.0.2.2:3000
```

모바일 앱과 백엔드가 모두 이 값을 공유합니다. Android 에뮬레이터에서 로컬 백엔드(localhost:3000)에 접속하기 위한 기본값입니다.

## 환경별 설정 변경

### Android 에뮬레이터 (기본값)
```bash
API_BASE_URL=http://10.0.2.2:3000
```

### iOS 시뮬레이터
```bash
API_BASE_URL=http://localhost:3000
```

### 실제 디바이스 (PC와 같은 Wi-Fi)
```bash
# PC의 로컬 IP 주소 확인 (Windows: ipconfig, Mac/Linux: ifconfig)
API_BASE_URL=http://192.168.1.100:3000
```

## 백엔드 서비스 시작 (선택사항)

앱을 완전히 테스트하려면 백엔드 서비스가 필요합니다:

```bash
# 프로젝트 루트 디렉토리에서
docker-compose up -d
```

이 명령어는 다음을 시작합니다:
- BFF (포트 3000)
- Core Service (포트 8000)
- ML Service (포트 8001)
- PostgreSQL (포트 5432)
- Redis (포트 6379)

## 문제 해결

### "Build failed due to use of deleted Android v1 embedding" 오류
✅ **해결됨**: MainActivity.kt 파일이 생성되었습니다.

### 네트워크 연결 오류
1. 백엔드 서비스가 실행 중인지 확인:
   ```bash
   docker-compose ps
   ```

2. Android 에뮬레이터에서 `10.0.2.2`가 작동하는지 확인:
   ```bash
   # 에뮬레이터 터미널에서
   ping 10.0.2.2
   ```

3. 방화벽에서 포트 3000이 열려있는지 확인

### 빌드 오류
```bash
cd mobile
flutter clean
flutter pub get
cd android
./gradlew clean
cd ..
flutter run
```

## 다음 단계

1. ✅ 앱 실행 확인
2. 📸 카메라/갤러리 권한 테스트
3. 🔍 품목 검색 기능 테스트
4. 📊 가격 정보 조회 테스트

## 추가 정보

- 상세 설정: `SETUP_GUIDE.md` 참고
- API 문서: `README.md` 참고
- 에러 처리: `mobile/docs/ERROR_HANDLING.md` 참고
