from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey, TIMESTAMP, Boolean, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Item(Base):
    """품목 테이블"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name_ko = Column(String(100), nullable=False, index=True)
    name_en = Column(String(100))
    category = Column(String(50), nullable=False, index=True)
    season_start = Column(Integer)  # 1-12 (월)
    season_end = Column(Integer)    # 1-12 (월)
    default_origin = Column(String(100))
    unit_default = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 관계
    prices = relationship("MarketPrice", back_populates="item")
    aliases = relationship("ItemAlias", back_populates="item")
    price_rule = relationship("PriceRule", back_populates="item", uselist=False)
    certifications = relationship("Certification", back_populates="item")
    distribution_stats = relationship("DistributionStats", back_populates="item")
    monthly_prices = relationship("MonthlyPrice", back_populates="item")

class Market(Base):
    """시장 테이블"""
    __tablename__ = "markets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(String(50))
    
    # 관계
    prices = relationship("MarketPrice", back_populates="market")
    aliases = relationship("ItemAlias", back_populates="market")

class MarketPrice(Base):
    """시장 가격 테이블"""
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    date = Column(Date, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    origin = Column(String(100))
    source = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 관계
    item = relationship("Item", back_populates="prices")
    market = relationship("Market", back_populates="prices")
    
    # 복합 인덱스 및 유니크 제약
    __table_args__ = (
        Index('idx_market_prices_item_date', 'item_id', 'date'),
        Index('idx_market_prices_market_date', 'market_id', 'date'),
        UniqueConstraint('item_id', 'market_id', 'date', name='uq_item_market_date'),
    )

class PriceRule(Base):
    """가격 규칙 테이블 (품목별 임계값)"""
    __tablename__ = "price_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False)
    high_threshold = Column(DECIMAL(3, 2), default=1.15)
    low_threshold = Column(DECIMAL(3, 2), default=0.90)
    min_days = Column(Integer, default=30)
    
    # 관계
    item = relationship("Item", back_populates="price_rule")

class ItemAlias(Base):
    """품목 별칭 테이블"""
    __tablename__ = "item_aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    raw_name = Column(String(200), nullable=False, index=True)
    confidence = Column(DECIMAL(3, 2), default=1.0)
    
    # 관계
    item = relationship("Item", back_populates="aliases")
    market = relationship("Market", back_populates="aliases")
    
    # 유니크 제약
    __table_args__ = (
        UniqueConstraint('market_id', 'raw_name', name='uq_market_raw_name'),
    )


# 공공데이터 API 통합 모델

class SpeciesCode(Base):
    """어종 코드 테이블"""
    __tablename__ = "species_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ko = Column(String(100), nullable=False, index=True)
    name_en = Column(String(100))
    category = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class TraceabilityCode(Base):
    """수산물이력제 품목코드 테이블"""
    __tablename__ = "traceability_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(100), nullable=False, index=True)
    registration_date = Column(Date, nullable=False)
    status = Column(String(20), server_default='active')
    created_at = Column(TIMESTAMP, server_default=func.now())


class Certification(Base):
    """인증 정보 테이블"""
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    cert_type = Column(String(20), nullable=False, index=True)  # 'quality', 'organic', 'gi'
    product_name = Column(String(100), nullable=False)
    company_name = Column(String(200))
    cert_number = Column(String(100), unique=True)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    region = Column(String(100))  # GI용
    is_active = Column(Boolean, server_default='true', index=True)
    item_id = Column(Integer, ForeignKey("items.id"), index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 관계
    item = relationship("Item", back_populates="certifications")
    
    # 인덱스
    __table_args__ = (
        Index('idx_certifications_product_name', 'product_name'),
    )


class ProhibitedSpecies(Base):
    """포획 금지 어종 테이블"""
    __tablename__ = "prohibited_species"
    
    id = Column(Integer, primary_key=True, index=True)
    species_code = Column(String(50), nullable=False, index=True)
    name_ko = Column(String(100), nullable=False, index=True)
    name_en = Column(String(100))
    prohibition_start = Column(Date, nullable=False)
    prohibition_end = Column(Date, nullable=False)
    reason = Column(String)
    # is_currently_prohibited는 GENERATED ALWAYS AS 컬럼으로 DB에서 자동 계산
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class DistributionStats(Base):
    """유통 통계 테이블"""
    __tablename__ = "distribution_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    auction_location = Column(String(100), nullable=False)
    origin = Column(String(100))
    quantity = Column(DECIMAL(10, 2))
    amount = Column(DECIMAL(12, 2))
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 관계
    item = relationship("Item", back_populates="distribution_stats")
    
    # 복합 인덱스 및 유니크 제약
    __table_args__ = (
        Index('idx_distribution_date', 'date'),
        Index('idx_distribution_item_date', 'item_id', 'date'),
        UniqueConstraint('item_id', 'auction_location', 'date', name='uq_item_auction_date'),
    )


class MonthlyPrice(Base):
    """월별 가격 테이블"""
    __tablename__ = "monthly_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    avg_price = Column(DECIMAL(10, 2), nullable=False)
    min_price = Column(DECIMAL(10, 2))
    max_price = Column(DECIMAL(10, 2))
    unit = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 관계
    item = relationship("Item", back_populates="monthly_prices")
    
    # 복합 인덱스 및 유니크 제약
    __table_args__ = (
        Index('idx_monthly_prices_period', 'year', 'month'),
        Index('idx_monthly_prices_item_period', 'item_id', 'year', 'month'),
        UniqueConstraint('item_id', 'year', 'month', name='uq_item_year_month'),
    )
