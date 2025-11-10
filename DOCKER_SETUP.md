# Docker 실행 가이드

## 문제 상황
```
unable to get image 'postgres:15': error during connect: 
Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/images/postgres:15/json": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**원인**: Docker Desktop이 실행되지 않음

## 해결 방법

### 1단계: Docker Desktop 시작

#### 방법 1: 시작 메뉴에서 실행
1. Windows 시작 메뉴 열기
2. "Docker Desktop" 검색
3. 클릭하여 실행
4. Docker Desktop이 완전히 시작될 때까지 대기 (1-2분)
5. 시스템 트레이에서 Docker 아이콘이 초록색이 되면 준비 완료

#### 방법 2: PowerShell에서 실행
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### 2단계: Docker 상태 확인
```bash
docker ps
```

정상이면 다음과 같이 출력됩니다:
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

### 3단계: 프로젝트 루트에서 Docker Compose 실행

**중요**: `mobile` 디렉토리가 아닌 **프로젝트 루트**에서 실행!

```bash
# 현재 위치 확인
pwd
# 출력: C:\Users\USER\Desktop\susissak

# 루트로 이동 (mobile 디렉토리에 있다면)
cd ..

# Docker Compose 실행
docker-compose up -d
```

## 백엔드 없이 앱만 테스트하기

Docker를 실행하지 않고도 앱 UI는 테스트할 수 있습니다:

```bash
cd mobile
flutter run -d emulator-5554
```

**결과**:
- ✅ 앱 UI 정상 작동
- ✅ 화면 탐색 가능
- ⚠️ API 호출은 실패 (네트워크 오류 표시)
- 🎨 로딩, 에러 처리 등 모든 UI 확인 가능

## Docker Compose 서비스 구성

프로젝트 루트의 `docker-compose.yml`에 정의된 서비스:

1. **postgres** (포트 5432) - 데이터베이스
2. **redis** (포트 6379) - 캐시
3. **core** (포트 8000) - Core Service API
4. **bff** (포트 3000) - Backend for Frontend
5. **ml** (포트 8001) - ML Service (이미지 인식)
6. **data-ingestion** - 데이터 수집 스케줄러

## 서비스 상태 확인

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f bff
```

## 서비스 중지

```bash
# 모든 서비스 중지
docker-compose down

# 데이터까지 삭제
docker-compose down -v
```

## 문제 해결

### Docker Desktop이 시작되지 않음
1. Windows 재시작
2. Docker Desktop 재설치
3. WSL 2 업데이트 확인

### 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

### 이미지 다운로드 실패
```bash
# Docker Hub 로그인 (필요시)
docker login

# 이미지 수동 다운로드
docker pull postgres:15
docker pull redis:7
```

## 요약

1. **Docker Desktop 시작** (필수)
2. **프로젝트 루트로 이동** (`cd C:\Users\USER\Desktop\susissak`)
3. **docker-compose up -d** 실행
4. **mobile 디렉토리로 이동** (`cd mobile`)
5. **flutter run** 실행

또는 백엔드 없이:
1. **mobile 디렉토리로 이동**
2. **flutter run** 실행 (UI만 테스트)
