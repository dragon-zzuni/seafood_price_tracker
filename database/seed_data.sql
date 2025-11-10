-- 추가 초기 데이터 및 샘플 데이터

-- 품목 별칭 예시 (가락시장)
INSERT INTO item_aliases (item_id, market_id, raw_name, confidence) VALUES
    (1, 1, '광어(대)', 1.0),
    (1, 1, '광어(중)', 1.0),
    (1, 1, '광어(소)', 1.0),
    (2, 1, '고등어', 1.0),
    (2, 1, '고등어(대)', 1.0),
    (3, 1, '조기', 1.0),
    (3, 1, '참조기', 1.0),
    (4, 1, '갈치', 1.0),
    (4, 1, '갈치(대)', 1.0),
    (5, 1, '오징어', 1.0);

-- 품목 별칭 예시 (노량진)
INSERT INTO item_aliases (item_id, market_id, raw_name, confidence) VALUES
    (1, 2, '광어', 1.0),
    (1, 2, '넙치', 1.0),
    (2, 2, '고등어', 1.0),
    (3, 2, '조기', 1.0),
    (4, 2, '갈치', 1.0),
    (5, 2, '오징어', 1.0),
    (6, 2, '꽃게', 1.0),
    (7, 2, '대하', 1.0),
    (8, 2, '전복', 1.0),
    (9, 2, '굴', 1.0);

-- 가격 규칙 예시 (일부 품목에 대해 커스텀 임계값)
INSERT INTO price_rules (item_id, high_threshold, low_threshold, min_days) VALUES
    (1, 1.20, 0.85, 30),  -- 광어: 더 넓은 범위
    (8, 1.10, 0.95, 30);  -- 전복: 더 좁은 범위

-- 샘플 가격 데이터 (최근 30일)
-- 실제 운영 시에는 Data Ingestion Service가 자동으로 수집
INSERT INTO market_prices (item_id, market_id, date, price, unit, origin, source) VALUES
    (1, 1, CURRENT_DATE, 18500, 'kg', '제주', '가락시장'),
    (1, 2, CURRENT_DATE, 19000, 'kg', '제주', '노량진수산시장'),
    (2, 1, CURRENT_DATE, 8500, 'kg', '동해', '가락시장'),
    (2, 2, CURRENT_DATE, 9000, 'kg', '동해', '노량진수산시장'),
    (3, 1, CURRENT_DATE, 15000, 'kg', '서해', '가락시장'),
    (4, 1, CURRENT_DATE, 22000, 'kg', '제주', '가락시장'),
    (5, 1, CURRENT_DATE, 12000, 'kg', '동해', '가락시장');
