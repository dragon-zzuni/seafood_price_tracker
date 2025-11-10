# Android v1 Embedding 오류 디버깅

## 문제 상황
`Build failed due to use of deleted Android v1 embedding` 오류가 계속 발생

## 확인한 사항
1. ✅ MainActivity.kt 생성됨 (v2 embedding 사용)
2. ✅ AndroidManifest.xml 정상
3. ✅ build.gradle.kts 정상
4. ✅ GeneratedPluginRegistrant.java 삭제됨
5. ✅ Flutter clean 실행됨

## 문제 원인
Flutter가 프로젝트를 v1 embedding으로 감지하는 조건:
1. `android/app/src/main/java/io/flutter/plugins/GeneratedPluginRegistrant.java` 존재 → **삭제함**
2. AndroidManifest.xml에 v1 embedding 메타데이터 존재 → **없음**
3. 플러그인이 v1 embedding 사용 → **확인 필요**

## 해결 방법

### 방법 1: 완전히 새로운 프로젝트 생성 (권장)
```bash
# 현재 디렉토리 밖에서
flutter create seafood_price_tracker_new

# lib 폴더 복사
cp -r mobile/lib seafood_price_tracker_new/
cp mobile/pubspec.yaml seafood_price_tracker_new/
cp mobile/.env seafood_price_tracker_new/
cp -r mobile/android/app/src/main/AndroidManifest.xml seafood_price_tracker_new/android/app/src/main/

# 새 프로젝트로 이동
cd seafood_price_tracker_new
flutter pub get
flutter run
```

### 방법 2: Android 폴더 완전 재생성
```bash
cd mobile

# Android 폴더 백업
mv android android_backup

# Android 플랫폼 재생성
flutter create --platforms=android .

# AndroidManifest.xml 복원
cp android_backup/app/src/main/AndroidManifest.xml android/app/src/main/

# MainActivity.kt 생성
mkdir -p android/app/src/main/kotlin/com/example/seafood_price_tracker
```

그 다음 MainActivity.kt 파일 생성:
```kotlin
package com.example.seafood_price_tracker

import io.flutter.embedding.android.FlutterActivity

class MainActivity: FlutterActivity()
```

```bash
flutter clean
flutter pub get
flutter run
```

### 방법 3: Flutter 캐시 완전 삭제
```bash
flutter clean
rm -rf ~/.gradle/caches/
rm -rf android/.gradle
rm -rf android/app/build
flutter pub get
flutter run
```

## 임시 해결책: Windows에서 실행
Android 에뮬레이터 대신 Windows 데스크톱으로 실행:
```bash
flutter run -d windows
```

이 방법은 UI 테스트에는 충분하며, Android 특정 기능(카메라 등)만 제외됩니다.
