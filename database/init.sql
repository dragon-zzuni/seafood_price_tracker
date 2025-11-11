-- 수산물 가격 추적 시스템 데이터베이스 스키마

-- 품목 테이블
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name_ko VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    category VARCHAR(50) NOT NULL,  -- fish, shellfish, crustacean, etc
    season_start INT,  -- 1-12 (월)
    season_end INT,    -- 1-12 (월)
    default_origin VARCHAR(100),
    unit_default VARCHAR(20),  -- kg, 마리, 상자
    created_at TIMESTAMP DEFAULT NOW()
);

-- 시장 테이블
CREATE TABLE markets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,  -- GARAK, NORYANGJIN
    type VARCHAR(50)  -- wholesale, retail
);

-- 시장 가격 테이블
CREATE TABLE market_prices (
    id SERIAL PRIMARY KEY,
    item_id INT REFERENCES items(id),
    market_id INT REFERENCES markets(id),
    date DATE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    origin VARCHAR(100),
    source VARCHAR(100),  -- 데이터 출처
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(item_id, market_id, date)
);

-- 가격 규칙 테이블 (품목별 임계값)
CREATE TABLE price_rules (
    id SERIAL PRIMARY KEY,
    item_id INT REFERENCES items(id) UNIQUE,
    high_threshold DECIMAL(3, 2) DEFAULT 1.15,  -- 높음 기준
    low_threshold DECIMAL(3, 2) DEFAULT 0.90,   -- 낮음 기준
    min_days INT DEFAULT 30  -- 평균 계산 기간
);

-- 품목 별칭 테이블
CREATE TABLE item_aliases (
    id SERIAL PRIMARY KEY,
    item_id INT REFERENCES items(id),
    market_id INT REFERENCES markets(id),
    raw_name VARCHAR(200) NOT NULL,  -- 원본 품목명
    confidence DECIMAL(3, 2) DEFAULT 1.0,  -- 매칭 신뢰도
    UNIQUE(market_id, raw_name)
);

-- 인덱스 생성
CREATE INDEX idx_market_prices_item_date ON market_prices(item_id, date DESC);
CREATE INDEX idx_market_prices_market_date ON market_prices(market_id, date DESC);
CREATE INDEX idx_item_aliases_raw_name ON item_aliases(raw_name);

-- 초기 데이터: 시장 정보
INSERT INTO markets (name, code, type) VALUES
    ('가락시장', 'GARAK', 'wholesale'),
    ('노량진수산시장', 'NORYANGJIN', 'retail');

-- 초기 데이터: 주요 품목
INSERT INTO items (name_ko, name_en, category, season_start, season_end, default_origin, unit_default) VALUES
    ('광어', 'Flounder', 'fish', 11, 2, '제주', 'kg'),
    ('우럭', 'Rockfish', 'fish', 3, 6, '서해', 'kg'),
    ('참돔', 'Red Seabream', 'fish', 4, 6, '남해', 'kg'),
    ('연어', 'Salmon', 'fish', 9, 11, '노르웨이', 'kg'),
    ('돌돔', 'Striped Beakfish', 'fish', 6, 8, '제주', 'kg'),
    ('감성돔', 'Black Porgy', 'fish', 10, 12, '남해', 'kg'),
    ('방어', 'Yellowtail Amberjack', 'fish', 11, 2, '제주', 'kg'),
    ('민어', 'Croaker', 'fish', 6, 8, '서해', 'kg'),
    ('농어', 'Sea Bass', 'fish', 5, 7, '서해', 'kg'),
    ('고등어', 'Mackerel', 'fish', 9, 12, '동해', 'kg'),
    ('대게', 'Snow Crab', 'crustacean', 11, 4, '동해', 'kg'),
    ('킹크랩', 'King Crab', 'crustacean', 11, 3, '러시아', 'kg'),
    ('코끼리조개', 'Geoduck', 'shellfish', 3, 5, '전남', 'kg'),
    ('왕우럭조개', 'King Turban Shell', 'shellfish', 5, 8, '제주', 'kg'),
    ('전복', 'Abalone', 'shellfish', 6, 9, '완도', '마리'),
    ('멍게', 'Sea Squirt', 'other', 4, 6, '통영', 'kg'),
    ('해삼', 'Sea Cucumber', 'other', 12, 2, '남해', 'kg'),
    ('개불', 'Spoon Worm', 'other', 2, 4, '서해', 'kg'),
    ('낙지', 'Octopus', 'cephalopod', 7, 10, '서해', 'kg'),
    ('참소라', 'Top Shell', 'shellfish', 7, 9, '제주', 'kg'),
    ('새우', 'Shrimp', 'crustacean', 5, 9, '서해', 'kg'),
    ('갑오징어', 'Cuttlefish', 'cephalopod', 4, 6, '남해', 'kg');

-- Materialized View: 일별 평균 가격 (차트용)
CREATE MATERIALIZED VIEW daily_avg_prices AS
SELECT 
    item_id,
    market_id,
    date,
    AVG(price) as avg_price,
    COUNT(*) as sample_count
FROM market_prices
GROUP BY item_id, market_id, date;

-- Materialized View 인덱스
CREATE INDEX idx_daily_avg_prices ON daily_avg_prices(item_id, market_id, date DESC);

-- 주석
COMMENT ON TABLE items IS '수산물 품목 정보';
COMMENT ON TABLE markets IS '수산시장 정보';
COMMENT ON TABLE market_prices IS '시장별 가격 데이터';
COMMENT ON TABLE price_rules IS '품목별 가격 태깅 임계값';
COMMENT ON TABLE item_aliases IS '시장별 품목명 별칭 매핑';
