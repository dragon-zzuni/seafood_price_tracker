from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey, TIMESTAMP, Index, UniqueConstraint
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
