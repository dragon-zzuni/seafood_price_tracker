# Requirements Document

## Introduction

수산물 가격 정보 추적 시스템(Seafood Price Tracker)은 사용자가 식재료(주로 수산물)를 선택하거나 사진으로 인식하면, 해당 품목의 산지 정보, 계절성, 가격 변동 추이, 주요 수산시장 시세를 제공하고 평소 대비 가격 상태를 태깅하는 모바일 애플리케이션입니다. 이 시스템은 소비자가 합리적인 구매 결정을 내릴 수 있도록 실시간 시장 데이터와 분석 정보를 제공합니다.

## Glossary

- **Mobile App**: 사용자가 직접 사용하는 Flutter 기반 모바일 애플리케이션
- **ML Service**: 이미지를 분석하여 수산물 품목을 인식하는 머신러닝 서비스
- **Core Service**: 품목 정보, 시장 가격, 태깅 로직을 처리하는 백엔드 도메인 서비스
- **BFF (Backend For Frontend)**: 모바일 앱과 백엔드 서비스 사이의 API Gateway
- **Data Ingestion Service**: 공공데이터 및 시장 사이트에서 가격 정보를 수집하는 배치 서비스
- **Item**: 수산물 품목 (예: 광어, 고등어, 조개)
- **Market**: 수산시장 (예: 가락시장, 노량진수산시장)
- **Price Tag**: 평소 대비 가격 상태 분류 (높음, 보통, 낮음)
- **Base Price**: 최근 30일 평균 가격
- **Season Period**: 특정 품목의 제철 기간
- **Origin**: 수산물의 산지 (예: 동해, 서해, 남해, 제주)

## Requirements

### Requirement 1: 이미지 기반 품목 인식

**User Story:** 사용자로서, 수산물 사진을 촬영하여 품목을 자동으로 인식하고 싶습니다. 그래야 품목명을 직접 검색하지 않고도 빠르게 정보를 확인할 수 있습니다.

#### Acceptance Criteria

1. WHEN 사용자가 Mobile App에서 카메라 버튼을 누르면, THE Mobile App SHALL 기기의 카메라 인터페이스를 활성화한다
2. WHEN 사용자가 이미지를 선택하거나 촬영을 완료하면, THE Mobile App SHALL 해당 이미지를 BFF에 업로드한다
3. WHEN BFF가 이미지를 수신하면, THE BFF SHALL ML Service에 이미지 인식을 요청한다
4. WHEN ML Service가 이미지를 수신하면, THE ML Service SHALL Detection 모듈로 수산물 영역을 탐지한다
5. WHEN Detection이 완료되면, THE ML Service SHALL Classification 모듈로 탐지된 영역의 품목을 분류한다
6. WHEN ML Service가 이미지를 분석하면, THE ML Service SHALL 신뢰도 점수와 함께 최대 4개의 품목 후보를 반환한다
7. WHEN 품목 후보 리스트가 반환되면, THE Mobile App SHALL 신뢰도 점수 순으로 정렬된 품목 리스트를 표시한다

### Requirement 2: 직접 품목 검색 및 선택

**User Story:** 사용자로서, 품목명을 직접 검색하여 선택하고 싶습니다. 그래야 사진 촬영이 어려운 상황에서도 정보를 조회할 수 있습니다.

#### Acceptance Criteria

1. WHEN 사용자가 검색창에 텍스트를 입력하면, THE Mobile App SHALL 입력된 텍스트와 일치하는 품목 리스트를 자동완성으로 표시한다
2. WHEN 자동완성 요청이 발생하면, THE BFF SHALL 200밀리초 이내에 최대 10개의 매칭 품목을 반환한다
3. THE Mobile App SHALL 품목을 카테고리별(생선, 조개류, 갑각류, 기타)로 분류하여 표시한다
4. WHEN 사용자가 품목을 선택하면, THE Mobile App SHALL 해당 품목의 상세 대시보드 화면으로 이동한다

### Requirement 3: 품목 기본 정보 표시

**User Story:** 사용자로서, 선택한 품목의 기본 정보(산지, 제철 기간)를 확인하고 싶습니다. 그래야 품목의 특성을 이해하고 구매 시기를 판단할 수 있습니다.

#### Acceptance Criteria

1. WHEN 사용자가 품목을 선택하면, THE Mobile App SHALL 품목의 한글명과 영문명을 표시한다
2. THE Mobile App SHALL 품목의 주요 산지 정보를 표시한다
3. THE Mobile App SHALL 품목의 제철 기간을 월 단위로 표시한다
4. WHEN 현재 날짜가 제철 기간에 포함되면, THE Mobile App SHALL "제철" 배지를 표시한다
5. WHEN 현재 날짜가 제철 기간에 포함되지 않으면, THE Mobile App SHALL "비성수기" 배지를 표시한다

### Requirement 4: 시장별 현재 가격 조회

**User Story:** 사용자로서, 주요 수산시장의 현재 가격을 확인하고 싶습니다. 그래야 어느 시장에서 구매하는 것이 유리한지 비교할 수 있습니다.

#### Acceptance Criteria

1. WHEN 품목 대시보드가 로드되면, THE Core Service SHALL 가락시장과 노량진수산시장의 최신 가격 데이터를 조회한다
2. THE Mobile App SHALL 각 시장의 가격을 단위(kg, 마리, 상자)와 함께 표시한다
3. WHEN 당일 가격 데이터가 존재하지 않으면, THE Core Service SHALL 최근 7일 이내의 가장 최신 데이터를 반환한다
4. WHEN 7일 이내 데이터가 존재하지 않으면, THE Mobile App SHALL "데이터 부족" 메시지를 표시한다
5. THE Mobile App SHALL 각 가격 데이터의 수집 날짜를 표시한다

### Requirement 5: 가격 추이 차트 제공

**User Story:** 사용자로서, 품목의 가격 변동 추이를 시각적으로 확인하고 싶습니다. 그래야 가격 패턴을 파악하고 구매 시기를 결정할 수 있습니다.

#### Acceptance Criteria

1. THE Mobile App SHALL 7일, 30일, 90일 기간 선택 옵션을 제공한다
2. WHEN 사용자가 기간을 선택하면, THE Mobile App SHALL 해당 기간의 가격 데이터를 라인 차트로 표시한다
3. THE Mobile App SHALL 시장별로 구분된 라인을 서로 다른 색상으로 표시한다
4. WHEN 차트 데이터 포인트를 터치하면, THE Mobile App SHALL 해당 날짜의 정확한 가격을 툴팁으로 표시한다
5. WHEN 선택한 기간의 데이터가 3개 미만이면, THE Mobile App SHALL "데이터 부족" 메시지를 표시한다

### Requirement 6: 가격 태깅 계산 및 표시

**User Story:** 사용자로서, 현재 가격이 평소 대비 높은지 낮은지 알고 싶습니다. 그래야 지금이 구매하기 좋은 시기인지 판단할 수 있습니다.

#### Acceptance Criteria

1. WHEN Core Service가 가격 태그를 계산하면, THE Core Service SHALL 최근 30일 평균 가격을 Base Price로 계산한다
2. WHEN 오늘 가격이 Base Price의 1.15배 이상이면, THE Core Service SHALL "높음" 태그를 반환한다
3. WHEN 오늘 가격이 Base Price의 0.9배 미만이면, THE Core Service SHALL "낮음" 태그를 반환한다
4. WHEN 오늘 가격이 Base Price의 0.9배 이상 1.15배 미만이면, THE Core Service SHALL "보통" 태그를 반환한다
5. THE Mobile App SHALL 가격 태그를 색상으로 구분하여 표시한다 (높음: 빨강, 보통: 회색, 낮음: 파랑)
6. THE Mobile App SHALL 가격 태그와 함께 Base Price 대비 비율을 백분율로 표시한다

### Requirement 7: 데이터 수집 및 갱신

**User Story:** 시스템 관리자로서, 시장 가격 데이터가 자동으로 수집되고 갱신되기를 원합니다. 그래야 사용자에게 최신 정보를 제공할 수 있습니다.

#### Acceptance Criteria

1. THE Data Ingestion Service SHALL 매일 08시 30분, 11시 30분, 15시 30분에 가격 데이터 수집을 실행한다
2. WHEN 수집 작업이 실행되면, THE Data Ingestion Service SHALL 공공데이터 포털 API에서 도매시장 경락가를 조회한다
3. WHEN 수집 작업이 실행되면, THE Data Ingestion Service SHALL 가락시장과 노량진수산시장 데이터를 수집한다
4. WHEN 원본 데이터를 수집하면, THE Data Ingestion Service SHALL 품목명을 내부 Item ID로 매핑한다
5. WHEN 품목명 매핑이 실패하면, THE Data Ingestion Service SHALL 실패 로그를 기록하고 다음 품목으로 진행한다
6. WHEN 데이터 정규화가 완료되면, THE Data Ingestion Service SHALL 데이터베이스에 가격 정보를 저장한다
7. WHEN 수집 작업이 완료되면, THE Data Ingestion Service SHALL 수집 성공 건수와 실패 건수를 로그에 기록한다

### Requirement 8: 품목 별칭 관리

**User Story:** 시스템 관리자로서, 시장마다 다른 품목명을 통합 관리하고 싶습니다. 그래야 동일한 품목의 가격을 정확하게 비교할 수 있습니다.

#### Acceptance Criteria

1. THE Core Service SHALL 품목별 별칭 매핑 테이블을 유지한다
2. WHEN Data Ingestion Service가 원본 품목명을 수신하면, THE Data Ingestion Service SHALL 별칭 테이블을 조회하여 표준 Item ID를 찾는다
3. WHEN 별칭 매핑이 존재하지 않으면, THE Data Ingestion Service SHALL 새로운 매핑 후보를 로그에 기록한다
4. THE Core Service SHALL 시장별로 서로 다른 별칭을 동일한 Item ID에 매핑할 수 있다

### Requirement 9: 응답 성능 최적화

**User Story:** 사용자로서, 품목 정보를 빠르게 확인하고 싶습니다. 그래야 시장에서 즉시 구매 결정을 내릴 수 있습니다.

#### Acceptance Criteria

1. WHEN 사용자가 품목 대시보드를 요청하면, THE BFF SHALL 500밀리초 이내에 응답을 반환한다
2. THE BFF SHALL 품목별 당일 가격 데이터를 Redis에 30분 동안 캐시한다
3. WHEN 캐시된 데이터가 존재하면, THE BFF SHALL 데이터베이스 조회 없이 캐시에서 데이터를 반환한다
4. WHEN 캐시된 데이터가 존재하지 않으면, THE BFF SHALL Core Service에서 데이터를 조회하고 캐시에 저장한다

### Requirement 10: 데이터 출처 표시

**User Story:** 사용자로서, 표시된 가격 정보의 출처와 날짜를 확인하고 싶습니다. 그래야 정보의 신뢰성을 판단할 수 있습니다.

#### Acceptance Criteria

1. THE Mobile App SHALL 각 가격 정보의 출처(시장명 또는 공공데이터)를 표시한다
2. THE Mobile App SHALL 각 가격 정보의 수집 날짜를 표시한다
3. WHEN 여러 출처의 데이터가 혼합되어 있으면, THE Mobile App SHALL 모든 출처를 쉼표로 구분하여 나열한다
4. THE Mobile App SHALL 데이터 출처 정보를 화면 하단에 작은 글씨로 표시한다

### Requirement 11: 오류 처리 및 사용자 피드백

**User Story:** 사용자로서, 시스템 오류가 발생했을 때 명확한 안내를 받고 싶습니다. 그래야 무엇이 문제인지 이해하고 대응할 수 있습니다.

#### Acceptance Criteria

1. WHEN 네트워크 오류가 발생하면, THE Mobile App SHALL "네트워크 연결을 확인해주세요" 메시지를 표시한다
2. WHEN 이미지 인식이 실패하면, THE Mobile App SHALL "품목을 인식할 수 없습니다. 직접 검색해주세요" 메시지를 표시한다
3. WHEN 서버 오류가 발생하면, THE Mobile App SHALL "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요" 메시지를 표시한다
4. WHEN 데이터 로딩 중이면, THE Mobile App SHALL 로딩 인디케이터를 표시한다
5. WHEN 오류 메시지를 표시하면, THE Mobile App SHALL 3초 후 자동으로 메시지를 숨긴다

### Requirement 12: 사용자 설정 관리

**User Story:** 사용자로서, 선호하는 시장과 단위를 설정하고 싶습니다. 그래야 내가 자주 이용하는 시장의 정보를 우선적으로 볼 수 있습니다.

#### Acceptance Criteria

1. THE Mobile App SHALL 설정 화면을 제공한다
2. THE Mobile App SHALL 우선 표시 시장 선택 옵션(가락시장 우선, 노량진 우선, 둘 다)을 제공한다
3. THE Mobile App SHALL 가격 단위 표시 선택 옵션(kg, 마리, 상자)을 제공한다
4. WHEN 사용자가 설정을 변경하면, THE Mobile App SHALL 변경사항을 로컬 저장소에 저장한다
5. WHEN 앱이 재시작되면, THE Mobile App SHALL 저장된 설정을 불러와 적용한다

### Requirement 13: ML 모델 교체 가능성

**User Story:** 개발팀으로서, 이미지 인식 모델을 쉽게 교체하거나 업그레이드하고 싶습니다. 그래야 더 나은 모델이 나왔을 때 빠르게 적용할 수 있습니다.

#### Acceptance Criteria

1. THE ML Service SHALL Detection 모듈과 Classification 모듈을 독립적인 인터페이스로 분리한다
2. THE ML Service SHALL 모델 타입(YOLO 단일, YOLO+CLIP)을 설정 파일로 선택할 수 있다
3. WHEN 새로운 모델을 배포하면, THE ML Service SHALL 기존 API 인터페이스를 변경하지 않고 모델만 교체할 수 있다
4. THE ML Service SHALL 모델 버전과 성능 메트릭을 로그에 기록한다

### Requirement 14: 코드 모듈화 및 유지보수성

**User Story:** 개발팀으로서, 각 기능이 독립적인 모듈로 구성되기를 원합니다. 그래야 특정 기능을 수정하거나 확장할 때 다른 부분에 영향을 주지 않습니다.

#### Acceptance Criteria

1. THE Core Service SHALL 품목 관리, 가격 조회, 태깅 계산을 별도 모듈로 분리한다
2. THE Data Ingestion Service SHALL 각 시장별 데이터 수집을 독립적인 Adapter 패턴으로 구현한다
3. THE BFF SHALL 각 도메인(품목, 가격, 인식)별로 라우터를 분리한다
4. THE Mobile App SHALL UI 컴포넌트, 상태 관리, API 클라이언트를 별도 레이어로 분리한다
5. WHEN 새로운 시장 데이터 소스를 추가하면, THE Data Ingestion Service SHALL 기존 Adapter를 수정하지 않고 새 Adapter만 추가할 수 있다
