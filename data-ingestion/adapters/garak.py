"""
가락시장 데이터 수집 어댑터
공공데이터 포털 API를 통해 가락시장 경락가 정보를 수집합니다.
"""
from datetime import datetime
from typing import List
import requests
import logging
from .base import MarketAdapter, RawPriceData

logger = logging.getLogger(__name__)


class GarakAdapter(MarketAdapter):
    """가락시장 어댑터"""
    
    MARKET_ID = 1  # 가락시장 ID
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Args:
            api_key: 공공데이터 포털 API 키
            base_url: API 기본 URL (기본값: 공공데이터 포털)
        """
        self.api_key = api_key
        self.base_url = base_url or "https://www.kamis.or.kr/service/price/xml.do"
        self.timeout = 30
    
    def get_market_id(self) -> int:
        """시장 ID 반환"""
        return self.MARKET_ID
    
    def fetch_data(self, date: datetime) -> List[RawPriceData]:
        """
        가락시장 데이터 수집
        
        Args:
            date: 조회 날짜
            
        Returns:
            원본 가격 데이터 리스트
        """
        logger.info(f"Fetching Garak market data for {date.strftime('%Y-%m-%d')}")
        
        try:
            # API 요청 파라미터
            params = {
                'action': 'dailyPriceByCategoryList',
                'p_cert_key': self.api_key,
                'p_cert_id': 'garak',
                'p_returntype': 'json',
                'p_product_cls_code': '02',  # 수산물 코드
                'p_regday': date.strftime('%Y-%m-%d'),
                'p_convert_kg_yn': 'Y',  # kg 단위로 변환
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return self._parse_response(data, date)
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch Garak market data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error parsing Garak market data: {str(e)}")
            raise
    
    def _parse_response(self, data: dict, date: datetime) -> List[RawPriceData]:
        """
        API 응답 파싱
        
        Args:
            data: API 응답 JSON
            date: 조회 날짜
            
        Returns:
            RawPriceData 리스트
        """
        results = []
        
        # API 응답 구조에 따라 데이터 추출
        items = data.get('data', {}).get('item', [])
        
        if not isinstance(items, list):
            items = [items] if items else []
        
        for item in items:
            try:
                # 품목명
                raw_name = item.get('item_name', '').strip()
                if not raw_name:
                    continue
                
                # 가격 (중간가 사용)
                price_str = item.get('dpr2', '0').replace(',', '')
                price = float(price_str)
                
                if price <= 0:
                    continue
                
                # 단위
                unit = item.get('unit', 'kg').strip()
                
                # 산지
                origin = item.get('origin', '').strip()
                
                results.append(RawPriceData(
                    raw_name=raw_name,
                    price=price,
                    unit=unit,
                    date=date,
                    origin=origin,
                    source='가락시장(공공데이터)'
                ))
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse item: {item}, error: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(results)} items from Garak market")
        return results
