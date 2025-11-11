"""
공공데이터 API 데이터 모델

공공데이터 포털에서 수집한 데이터를 표현하는 모델 클래스들을 제공합니다.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


# ============================================================================
# Price Data Models (가격 데이터)
# ============================================================================

@dataclass
class DailyPrice:
    """일별 경락가격
    
    KAMIS API 등에서 수집한 일별 도매시장 경락가격 데이터
    """
    item_id: int
    market_id: int
    price: float
    unit: str
    origin: str
    date: date
    quantity: Optional[float] = None
    source: str = "공공데이터"
    
    def __post_init__(self):
        """데이터 검증"""
        if self.price < 0:
            raise ValueError(f"가격은 0 이상이어야 합니다: {self.price}")
        if self.price > 1_000_000:
            raise ValueError(f"가격이 비정상적으로 높습니다: {self.price}")


@dataclass
class MonthlyPrice:
    """월별 평균가격
    
    월별 농축수산물 도매가격 추세 데이터
    """
    item_id: int
    year: int
    month: int
    avg_price: float
    min_price: float
    max_price: float
    unit: str
    
    def __post_init__(self):
        """데이터 검증"""
        if not (1 <= self.month <= 12):
            raise ValueError(f"월은 1-12 사이여야 합니다: {self.month}")
        if self.year < 2000 or self.year > 2100:
            raise ValueError(f"연도가 유효하지 않습니다: {self.year}")
        if self.min_price > self.avg_price or self.avg_price > self.max_price:
            raise ValueError(
                f"가격 범위가 잘못되었습니다: min={self.min_price}, "
                f"avg={self.avg_price}, max={self.max_price}"
            )


@dataclass
class DistributionStats:
    """유통 통계
    
    수산물유통종합정보 API에서 수집한 위판장별 통계 데이터
    """
    item_id: int
    auction_location: str
    origin: str
    quantity: float
    amount: float
    date: date
    
    def __post_init__(self):
        """데이터 검증"""
        if self.quantity < 0:
            raise ValueError(f"수량은 0 이상이어야 합니다: {self.quantity}")
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")


# ============================================================================
# Metadata Models (메타데이터)
# ============================================================================

@dataclass
class SpeciesCode:
    """어종 코드
    
    표준 어종 코드와 명칭 매핑 정보
    """
    code: str
    name_ko: str
    name_en: str
    category: str
    created_at: date
    
    def __post_init__(self):
        """데이터 검증"""
        if not self.code or not self.code.strip():
            raise ValueError("어종 코드는 필수입니다")
        if not self.name_ko or not self.name_ko.strip():
            raise ValueError("한글 명칭은 필수입니다")


@dataclass
class TraceabilityCode:
    """이력제 품목 코드
    
    수산물이력제 품목코드 정보
    """
    code: str
    product_name: str
    registration_date: date
    status: str = "active"
    
    def __post_init__(self):
        """데이터 검증"""
        if not self.code or not self.code.strip():
            raise ValueError("품목 코드는 필수입니다")
        if not self.product_name or not self.product_name.strip():
            raise ValueError("품목명은 필수입니다")
        if self.status not in ["active", "inactive"]:
            raise ValueError(f"상태는 active 또는 inactive여야 합니다: {self.status}")


# ============================================================================
# Certification Models (인증 정보)
# ============================================================================

@dataclass
class Certification:
    """인증 정보
    
    품질인증, 유기인증, 지리적표시 등의 인증 정보
    """
    cert_type: str  # 'quality', 'organic', 'gi'
    product_name: str
    company_name: str
    cert_number: str
    valid_from: date
    valid_until: date
    region: Optional[str] = None  # GI용
    is_active: bool = True
    item_id: Optional[int] = None
    
    def __post_init__(self):
        """데이터 검증"""
        valid_types = ['quality', 'organic', 'gi']
        if self.cert_type not in valid_types:
            raise ValueError(
                f"인증 타입은 {valid_types} 중 하나여야 합니다: {self.cert_type}"
            )
        
        if not self.product_name or not self.product_name.strip():
            raise ValueError("품목명은 필수입니다")
        
        if not self.cert_number or not self.cert_number.strip():
            raise ValueError("인증번호는 필수입니다")
        
        if self.valid_from > self.valid_until:
            raise ValueError(
                f"유효기간이 잘못되었습니다: {self.valid_from} ~ {self.valid_until}"
            )
    
    def is_expired(self, check_date: Optional[date] = None) -> bool:
        """인증 만료 여부 확인
        
        Args:
            check_date: 확인할 날짜 (기본값: 오늘)
            
        Returns:
            bool: 만료 여부
        """
        if check_date is None:
            check_date = date.today()
        return check_date > self.valid_until
    
    def is_valid(self, check_date: Optional[date] = None) -> bool:
        """인증 유효 여부 확인
        
        Args:
            check_date: 확인할 날짜 (기본값: 오늘)
            
        Returns:
            bool: 유효 여부
        """
        if check_date is None:
            check_date = date.today()
        return (
            self.is_active and
            self.valid_from <= check_date <= self.valid_until
        )


# ============================================================================
# Regulation Models (규제 정보)
# ============================================================================

@dataclass
class ProhibitedSpecies:
    """포획 금지 어종
    
    포획 금지 어종 정보 및 금지 기간
    """
    species_code: str
    name_ko: str
    name_en: str
    prohibition_start: date
    prohibition_end: date
    reason: str
    
    def __post_init__(self):
        """데이터 검증"""
        if not self.species_code or not self.species_code.strip():
            raise ValueError("어종 코드는 필수입니다")
        
        if not self.name_ko or not self.name_ko.strip():
            raise ValueError("한글 명칭은 필수입니다")
        
        if self.prohibition_start > self.prohibition_end:
            raise ValueError(
                f"금지 기간이 잘못되었습니다: "
                f"{self.prohibition_start} ~ {self.prohibition_end}"
            )
    
    def is_currently_prohibited(self, check_date: Optional[date] = None) -> bool:
        """현재 금지 상태 여부 확인
        
        Args:
            check_date: 확인할 날짜 (기본값: 오늘)
            
        Returns:
            bool: 금지 상태 여부
        """
        if check_date is None:
            check_date = date.today()
        return self.prohibition_start <= check_date <= self.prohibition_end
    
    def get_status_message(self, check_date: Optional[date] = None) -> str:
        """상태 메시지 반환
        
        Args:
            check_date: 확인할 날짜 (기본값: 오늘)
            
        Returns:
            str: 상태 메시지
        """
        if check_date is None:
            check_date = date.today()
        
        if check_date < self.prohibition_start:
            return f"금지 예정 ({self.prohibition_start}부터)"
        elif check_date > self.prohibition_end:
            return f"금지 해제됨 ({self.prohibition_end}까지)"
        else:
            return f"포획 금지 중 ({self.prohibition_end}까지)"


# ============================================================================
# Helper Functions
# ============================================================================

def validate_price_range(price: float, min_price: float = 0, max_price: float = 1_000_000) -> bool:
    """가격 범위 검증
    
    Args:
        price: 검증할 가격
        min_price: 최소 가격
        max_price: 최대 가격
        
    Returns:
        bool: 유효 여부
    """
    return min_price <= price <= max_price


def validate_item_name(name: str) -> bool:
    """품목명 유효성 검증
    
    Args:
        name: 검증할 품목명
        
    Returns:
        bool: 유효 여부
    """
    if not name or not name.strip():
        return False
    
    # 최소 길이 체크
    if len(name.strip()) < 2:
        return False
    
    # 특수문자만으로 구성되지 않았는지 체크
    if not any(c.isalnum() or c in '가-힣' for c in name):
        return False
    
    return True


def validate_date_format(date_obj: date) -> bool:
    """날짜 형식 검증
    
    Args:
        date_obj: 검증할 날짜
        
    Returns:
        bool: 유효 여부
    """
    # 합리적인 범위 체크 (2000년 ~ 현재+10년)
    min_year = 2000
    max_year = datetime.now().year + 10
    
    return min_year <= date_obj.year <= max_year
