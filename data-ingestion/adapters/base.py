from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from dataclasses import dataclass

@dataclass
class RawPriceData:
    """원본 가격 데이터"""
    raw_name: str
    price: float
    unit: str
    date: datetime
    origin: str = ""
    source: str = ""

class MarketAdapter(ABC):
    """시장 데이터 수집 어댑터 기본 클래스"""
    
    @abstractmethod
    def fetch_data(self, date: datetime) -> List[RawPriceData]:
        """시장 데이터 수집"""
        pass
    
    @abstractmethod
    def get_market_id(self) -> int:
        """시장 ID 반환"""
        pass
