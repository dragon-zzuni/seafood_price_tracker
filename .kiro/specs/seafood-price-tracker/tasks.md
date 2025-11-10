# Implementation Plan

- [x] 1. 프로젝트 구조 및 기본 인프라 설정





  - 각 서비스별 디렉토리 구조 생성 (bff, core-service, ml-service, data-ingestion, mobile)
  - Docker 및 docker-compose 설정 파일 작성
  - PostgreSQL 데이터베이스 스키마 생성 스크립트 작성
  - Redis 연결 설정
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [x] 2. Core Service - 데이터베이스 모델 및 리포지토리 구현





  - SQLAlchemy ORM 모델 정의 (items, markets, market_prices, price_rules, item_aliases)
  - 리포지토리 패턴으로 데이터 접근 레이어 구현
  - 데이터베이스 마이그레이션 스크립트 작성 (Alembic)
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 8.1, 8.2_

- [x] 3. Core Service - 품목 관리 모듈




- [x] 3.1 품목 검색 API 구현


  - 자동완성 검색 엔드포인트 (`GET /items?query={query}`)
  - 품목 상세 조회 엔드포인트 (`GET /items/{id}`)
  - 카테고리별 필터링 기능
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 3.2 품목 별칭 매칭 모듈 구현


  - AliasMatcher 클래스 작성 (정확 매칭 + 유사도 매칭)
  - Levenshtein distance 기반 유사도 계산
  - 매칭 실패 로그 기록
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 3.3 품목 관리 단위 테스트






  - 검색 기능 테스트
  - 별칭 매칭 테스트
  - _Requirements: 2.1, 8.2_


- [x] 4. Core Service - 가격 조회 및 태깅 모듈




- [x] 4.1 가격 조회 API 구현


  - 시장별 최신 가격 조회 로직
  - 데이터 없을 때 최근 7일 내 데이터 대체 로직
  - Materialized View를 활용한 가격 추이 조회
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2_

- [x] 4.2 가격 태깅 계산 로직 구현


  - PriceEvaluator 클래스 작성
  - 최근 30일 평균 가격 계산
  - 품목별 임계값 적용 (기본값: 1.15/0.90)
  - 태그 결정 로직 (높음/보통/낮음)
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 4.3 품목 대시보드 API 구현


  - 품목 정보 + 현재 가격 + 태그 + 추이 통합 엔드포인트
  - 제철 여부 계산 로직
  - 데이터 출처 정보 포함
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.5, 6.5, 6.6, 10.1, 10.2, 10.3_

- [ ]* 4.4 가격 태깅 단위 테스트
  - 높음/보통/낮음 태그 계산 테스트
  - Base price 계산 테스트
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 5. Data Ingestion Service - 어댑터 패턴 구현






- [x] 5.1 Base Adapter 인터페이스 정의

  - MarketAdapter 추상 클래스 작성
  - fetch_data, get_market_id 메서드 정의
  - _Requirements: 14.2, 14.5_


- [x] 5.2 가락시장 어댑터 구현

  - GarakAdapter 클래스 작성
  - 공공데이터 API 호출 로직
  - 응답 파싱 및 RawPriceData 변환
  - _Requirements: 7.1, 7.2, 7.3_


- [x] 5.3 노량진 어댑터 구현

  - NoryangjinAdapter 클래스 작성
  - 웹 스크래핑 로직 (BeautifulSoup 또는 Selenium)
  - HTML 파싱 및 데이터 추출
  - _Requirements: 7.1, 7.2, 7.3_


- [x] 5.4 데이터 정규화 모듈 구현

  - DataNormalizer 클래스 작성
  - 품목명 매핑 (AliasMatcher 활용)
  - 단위 변환 (kg, 마리, 상자 표준화)
  - _Requirements: 7.4, 7.5, 8.2_


- [x] 5.5 배치 스케줄러 구현

  - APScheduler를 사용한 스케줄링 (08:30, 11:30, 15:30)
  - 모든 어댑터 순회 실행
  - 성공/실패 로그 기록
  - 개별 어댑터 실패 시 다른 어댑터 계속 실행
  - _Requirements: 7.1, 7.6, 7.7_

- [ ]* 5.6 Data Ingestion 통합 테스트
  - 각 어댑터의 데이터 수집 테스트
  - 정규화 로직 테스트
  - _Requirements: 7.2, 7.4_

- [x] 6. BFF - API Gateway 구현




- [x] 6.1 NestJS 프로젝트 설정


  - 프로젝트 초기화 및 모듈 구조 생성
  - items, prices, recognition 모듈 분리
  - Swagger 문서 설정
  - _Requirements: 14.3_

- [x] 6.2 품목 관련 엔드포인트 구현

  - `GET /api/items?query={query}` - Core Service 프록시
  - `GET /api/items/{id}` - Core Service 프록시
  - 응답 포맷 변환 (모바일 친화적)
  - _Requirements: 2.1, 2.2, 2.4_

- [x] 6.3 대시보드 엔드포인트 구현

  - `GET /api/items/{id}/dashboard` - Core Service 호출
  - 응답 데이터 통합 및 포맷팅
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 6.5_

- [x] 6.4 Redis 캐싱 레이어 구현

  - Cache-Aside 패턴 적용
  - 품목 검색 결과 캐싱 (30분 TTL)
  - 대시보드 데이터 캐싱 (30분 TTL)
  - 캐시 키 전략 구현
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ]* 6.5 BFF 통합 테스트
  - 각 엔드포인트 응답 검증
  - 캐싱 동작 테스트
  - _Requirements: 9.2, 9.3_


- [x] 7. ML Service - 이미지 인식 파이프라인 구현



- [x] 7.1 모델 인터페이스 정의


  - DetectionModel 추상 클래스 작성
  - ClassificationModel 추상 클래스 작성
  - Strategy 패턴으로 모델 교체 가능하게 설계
  - _Requirements: 13.1, 13.3_

- [x] 7.2 YOLO Detection 모듈 구현


  - YOLODetector 클래스 작성
  - 모델 로딩 및 추론 로직
  - BoundingBox 결과 파싱
  - _Requirements: 1.4, 13.2_

- [x] 7.3 YOLO Classification 모듈 구현


  - YOLOClassifier 클래스 작성
  - 품목 분류 로직
  - 신뢰도 점수 계산
  - _Requirements: 1.5, 1.6_

- [x] 7.4 이미지 전처리 모듈 구현


  - 이미지 크기 검증 (최대 5MB)
  - 리사이징 (640x640)
  - 정규화 및 포맷 변환
  - _Requirements: 1.2_

- [x] 7.5 Recognition Pipeline 통합


  - RecognitionPipeline 클래스 작성
  - Detection → Classification 파이프라인 구현
  - 신뢰도 필터링 (threshold > 0.3)
  - Top-4 결과 반환
  - _Requirements: 1.4, 1.5, 1.6, 1.7_

- [x] 7.6 이미지 인식 API 엔드포인트


  - `POST /recognize` 엔드포인트 구현
  - 이미지 업로드 처리
  - 인식 결과 JSON 응답
  - _Requirements: 1.3, 1.6, 1.7_

- [ ]* 7.7 ML Service 단위 테스트
  - Detection 모듈 테스트
  - Classification 모듈 테스트
  - Pipeline 통합 테스트
  - _Requirements: 1.4, 1.5, 1.6_

- [x] 8. BFF - 이미지 인식 프록시 구현



- [x] 8.1 이미지 업로드 엔드포인트


  - `POST /api/recognition` 구현
  - Multipart 파일 업로드 처리
  - ML Service로 프록시
  - _Requirements: 1.2, 1.3_

- [x] 8.2 인식 결과 후처리


  - ML Service 응답을 모바일 친화적 포맷으로 변환
  - 품목 ID 매핑 (Core Service 조회)
  - 에러 처리 및 사용자 메시지 변환
  - _Requirements: 1.7, 11.2_

- [x] 9. Mobile App - Flutter 프로젝트 설정




- [x] 9.1 프로젝트 초기화 및 구조 설정


  - Flutter 프로젝트 생성
  - 디렉토리 구조 설정 (presentation, application, domain, infrastructure)
  - 의존성 추가 (riverpod, dio, fl_chart, image_picker)
  - _Requirements: 14.4_


- [x] 9.2 API 클라이언트 구현

  - ApiClient 클래스 작성
  - dio를 사용한 HTTP 요청 처리
  - 에러 핸들링 및 재시도 로직
  - _Requirements: 11.1, 11.3_


- [x] 9.3 도메인 모델 정의

  - Item, MarketPrice, PriceTag, ItemDashboard 모델 작성
  - JSON 직렬화/역직렬화 (json_serializable)
  - _Requirements: 2.1, 3.1, 4.1, 6.5_

- [x] 10. Mobile App - 품목 검색 기능




- [x] 10.1 검색 UI 구현


  - ItemSearchBar 위젯 작성
  - 자동완성 리스트 표시
  - 카테고리 필터 UI
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 10.2 검색 상태 관리


  - ItemProvider (Riverpod) 작성
  - 검색 쿼리 디바운싱 (300ms)
  - 로딩 상태 및 에러 처리
  - _Requirements: 2.1, 2.2, 11.1_

- [x] 10.3 홈 화면 구현


  - HomeScreen 작성
  - 검색창 + 카메라 버튼 배치
  - 인기 품목 카드 슬라이더 (선택 사항)
  - _Requirements: 2.1, 2.3_

- [x] 11. Mobile App - 이미지 인식 기능



- [x] 11.1 카메라 및 갤러리 연동


  - image_picker 패키지 사용
  - 카메라 촬영 및 갤러리 선택 기능
  - 권한 요청 처리
  - _Requirements: 1.1, 1.2_

- [x] 11.2 이미지 업로드 및 인식


  - RecognitionProvider (Riverpod) 작성
  - 이미지를 BFF에 업로드
  - 인식 중 로딩 인디케이터 표시
  - _Requirements: 1.2, 1.3, 11.4_

- [x] 11.3 인식 결과 화면


  - RecognitionResultScreen 작성
  - 후보 품목 리스트 표시 (신뢰도 순)
  - 품목 선택 시 대시보드로 이동
  - _Requirements: 1.7, 2.4_


- [x] 12. Mobile App - 품목 대시보드 화면





- [x] 12.1 대시보드 데이터 로딩

  - DashboardProvider (Riverpod) 작성
  - BFF에서 대시보드 데이터 조회
  - 로딩 및 에러 상태 관리
  - _Requirements: 3.1, 4.1, 6.5, 11.4_

- [x] 12.2 품목 기본 정보 위젯


  - 품목명 (한글/영문) 표시
  - 산지 정보 표시
  - 제철/비성수기 배지 표시
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_



- [x] 12.3 가격 카드 위젯

  - PriceCard 위젯 작성
  - 시장별 가격 표시 (가락/노량진)
  - 가격 태그 배지 (높음/보통/낮음) 색상 구분
  - 단위 및 날짜 표시

  - _Requirements: 4.1, 4.2, 4.5, 6.5, 6.6_

- [x] 12.4 가격 추이 차트 위젯

  - PriceChart 위젯 작성 (fl_chart 사용)
  - 7일/30일/90일 기간 선택 탭
  - 시장별 라인 차트 (색상 구분)
  - 데이터 포인트 터치 시 툴팁 표시
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_




- [x] 12.5 데이터 출처 표시

  - 화면 하단에 출처 정보 표시
  - 수집 날짜 표시


  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 12.6 대시보드 화면 통합




  - ItemDashboardScreen 작성
  - 모든 위젯 배치 및 스크롤 처리
  - 새로고침 기능 (pull-to-refresh)
  - _Requirements: 3.1, 4.1, 5.1, 6.5_

- [x] 13. Mobile App - 사용자 설정 기능





- [x] 13.1 설정 화면 UI

  - SettingsScreen 작성
  - 우선 표시 시장 선택 (가락/노량진/둘 다)
  - 가격 단위 선택 (kg/마리/상자)
  - _Requirements: 12.1, 12.2, 12.3_



- [x] 13.2 설정 저장 및 로딩




  - SettingsProvider (Riverpod) 작성
  - SharedPreferences를 사용한 로컬 저장
  - 앱 시작 시 설정 로딩


  - _Requirements: 12.4, 12.5_

- [x] 13.3 설정 적용




  - 대시보드에서 설정된 시장 우선 표시
  - 가격 단위 변환 적용
  - _Requirements: 12.2, 12.3_

- [x] 14. 에러 처리 및 사용자 피드백




- [x] 14.1 Core Service 에러 핸들링


  - 커스텀 예외 클래스 정의 (ItemNotFoundException, PriceDataNotFoundException 등)
  - FastAPI 예외 핸들러 구현
  - 표준 JSON 에러 응답 포맷
  - _Requirements: 11.1, 11.2, 11.3_



- [x] 14.2 BFF 에러 핸들링





  - NestJS 예외 필터 구현
  - Core/ML Service 오류를 사용자 친화적 메시지로 변환
  - 5xx 오류 상세 정보 숨김


  - _Requirements: 11.1, 11.2, 11.3_

- [x] 14.3 Mobile App 에러 UI




  - 네트워크 오류 메시지 및 재시도 버튼
  - 인식 실패 시 직접 검색 유도


  - 데이터 없음 안내 메시지
  - 3초 자동 숨김 스낵바
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 14.4 로딩 인디케이터





  - 데이터 로딩 중 스피너 표시
  - 이미지 인식 중 프로그레스 표시
  - _Requirements: 11.4_

- [ ] 15. 배포 및 인프라 설정
- [ ] 15.1 Docker 이미지 빌드
  - 각 서비스별 Dockerfile 작성
  - 멀티스테이지 빌드로 이미지 크기 최적화
  - _Requirements: 14.1, 14.2, 14.3_

- [ ] 15.2 docker-compose 통합
  - 모든 서비스 통합 docker-compose.yml 작성
  - 환경 변수 설정
  - 볼륨 및 네트워크 구성
  - _Requirements: 14.1, 14.2, 14.3_

- [ ] 15.3 데이터베이스 초기화
  - 초기 데이터 시드 스크립트 작성 (주요 품목, 시장 정보)
  - Materialized View 생성 스크립트
  - _Requirements: 3.1, 4.1_

- [ ]* 15.4 CI/CD 파이프라인 설정
  - GitHub Actions 워크플로우 작성
  - 테스트 자동화
  - Docker 이미지 빌드 및 푸시
  - _Requirements: 14.1_

- [ ] 16. 성능 최적화 및 모니터링
- [ ] 16.1 데이터베이스 인덱스 최적화
  - 자주 조회되는 컬럼에 인덱스 추가
  - 쿼리 실행 계획 분석 및 최적화
  - _Requirements: 9.1_

- [ ] 16.2 Materialized View 갱신 스케줄
  - 일별 평균 가격 Materialized View 생성
  - 매일 새벽 자동 갱신 스크립트
  - _Requirements: 5.2, 9.1_

- [ ]* 16.3 로깅 및 메트릭 수집
  - 구조화된 로깅 설정 (structlog)
  - Prometheus 메트릭 엔드포인트 추가
  - API 응답 시간, 인식 성공률 메트릭
  - _Requirements: 7.7, 13.4_

- [ ]* 16.4 성능 테스트
  - Locust를 사용한 부하 테스트
  - 목표: 100 동시 사용자, 500ms 평균 응답
  - _Requirements: 9.1_

- [ ] 17. 통합 및 E2E 테스트
- [ ]* 17.1 백엔드 통합 테스트
  - BFF → Core Service 통합 테스트
  - BFF → ML Service 통합 테스트
  - Data Ingestion → Database 통합 테스트
  - _Requirements: 1.3, 2.1, 4.1, 7.1_

- [ ]* 17.2 Mobile App E2E 테스트
  - 검색 → 선택 → 대시보드 플로우 테스트
  - 이미지 인식 → 선택 → 대시보드 플로우 테스트
  - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [ ] 18. 문서화 및 최종 점검
- [ ] 18.1 API 문서 작성
  - Swagger/OpenAPI 문서 완성
  - 각 엔드포인트 예시 요청/응답 추가
  - _Requirements: 2.1, 3.1, 4.1_

- [ ] 18.2 README 및 설치 가이드
  - 프로젝트 개요 및 아키텍처 설명
  - 로컬 개발 환경 설정 가이드
  - Docker를 사용한 배포 가이드
  - _Requirements: 14.1_

- [ ]* 18.3 운영 가이드
  - 데이터 수집 모니터링 방법
  - 장애 대응 절차
  - 백업 및 복구 절차
  - _Requirements: 7.7_
