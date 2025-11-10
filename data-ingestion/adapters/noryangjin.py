"""
노량진수산시장 데이터 수집 어댑터
웹 스크래핑을 통해 노량진수산시장 가격 정보를 수집합니다.
"""
from datetime import datetime
from typing import List
import requests
from bs4 import BeautifulSoup
import logging
import re
from .base import MarketAdapter, RawPriceData

logger = logging.getLogger(__name__)


class NoryangjinAdapter(MarketAdapter):
    """노량진수산시장 어댑터"""
    
    MARKET_ID = 2  # 노량진수산시장 ID
    
    def __init__(self, base_url: str = None):
        """
        Args:
            base_url: 노량진수산시장 가격 정보 페이지 URL
        """
        # 실제 노량진수산시장 웹사이트 URL (예시)
        self.base_url = base_url or "http://www.noryangjin.co.kr/price/list"
        self.timeout = 30
    
    def get_market_id(self) -> int:
        """시장 ID 반환"""
        return self.MARKET_ID
    
    def fetch_data(self, date: datetime) -> List[RawPriceData]:
        """
        노량진수산시장 데이터 수집
        
        Args:
            date: 조회 날짜
            
        Returns:
            원본 가격 데이터 리스트
        """
        logger.info(f"Fetching Noryangjin market data for {date.strftime('%Y-%m-%d')}")
        
        try:
            # 웹페이지 요청
            response = requests.get(
                self.base_url,
                params={'date': date.strftime('%Y%m%d')},
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            # HTML 파싱
            return self._parse_html(response.text, date)
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch Noryangjin market data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error parsing Noryangjin market data: {str(e)}")
            raise
    
    def _parse_html(self, html: str, date: datetime) -> List[RawPriceData]:
        """
        HTML 파싱하여 가격 데이터 추출
        
        Args:
            html: HTML 문자열
            date: 조회 날짜
            
        Returns:
            RawPriceData 리스트
        """
        results = []
        soup = BeautifulSoup(html, 'lxml')
        
        # 가격 테이블 찾기 (실제 웹사이트 구조에 맞게 수정 필요)
        # 예시: <table class="price-table">
        price_table = soup.find('table', class_='price-table')
        
        if not price_table:
            logger.warning("Price table not found in HTML")
            return results
        
        # 테이블 행 순회
        rows = price_table.find_all('tr')[1:]  # 헤더 제외
        
        for row in rows:
            try:
                cols = row.find_all('td')
                
                if len(cols) < 4:
                    continue
                
                # 품목명
                raw_name = cols[0].get_text(strip=True)
                if not raw_name:
                    continue
                
                # 산지
                origin = cols[1].get_text(strip=True)
                
                # 규격/단위
                unit_text = cols[2].get_text(strip=True)
                unit = self._extract_unit(unit_text)
                
                # 가격
                price_text = cols[3].get_text(strip=True)
                price = self._extract_price(price_text)
                
                if price <= 0:
                    continue
                
                results.append(RawPriceData(
                    raw_name=raw_name,
                    price=price,
                    unit=unit,
                    date=date,
                    origin=origin,
                    source='노량진수산시장'
                ))
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse row: {row}, error: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(results)} items from Noryangjin market")
        return results
    
    def _extract_price(self, price_text: str) -> float:
        """
        가격 텍스트에서 숫자 추출
        
        Args:
            price_text: 가격 문자열 (예: "18,500원", "18500")
            
        Returns:
            가격 (float)
        """
        # 숫자만 추출
        numbers = re.findall(r'\d+', price_text.replace(',', ''))
        if numbers:
            return float(''.join(numbers))
        return 0.0
    
    def _extract_unit(self, unit_text: str) -> str:
        """
        단위 텍스트에서 표준 단위 추출
        
        Args:
            unit_text: 단위 문자열 (예: "1kg", "10마리", "1상자")
            
        Returns:
            표준 단위
        """
        unit_text = unit_text.lower()
        
        if 'kg' in unit_text or '킬로' in unit_text:
            return 'kg'
        elif '마리' in unit_text or 'ea' in unit_text:
            return '마리'
        elif '상자' in unit_text or 'box' in unit_text:
            return '상자'
        else:
            return 'kg'  # 기본값
