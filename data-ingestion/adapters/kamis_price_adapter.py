"""
KAMIS 도매시장 경락가격 어댑터

한국농수산식품유통공사(KAMIS) API를 통해 도매시장별 경락가격 데이터를 수집합니다.

API 정보:
- 제공기관: 한국농수산식품유통공사
- 데이터: 도매시장별 일별 경락가격
- 품목: 수산물 (활어, 선어, 냉동 등)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

from .public_data_base import BasePublicDataAdapter, DataCategory
from .public_data_models import DailyPrice

logger = logging.getLogger(__name__)


class KamisPriceAdapter(BasePublicDataAdapter):
    """KAMIS 도매시장 경락가격 어댑터
    
    도매시장별 수산물 경락가격을 수집합니다.
    """
    
    # KAMIS API 엔드포인트
    ENDPOINT = "/price/wholesale/daily"
    
    # 수산물 카테고리 코드
    SEAFOOD_CATEGORY = "400"  # KAMIS 수산물 카테고리 코드
    
    def __init__(self, api_key: str, base_url: str = "http://www.kamis.or.kr/service/price"):
        """
        Args:
            api_key: KAMIS API 키
            base_url: API 기본 URL (기본값: KAMIS 공식 URL)
        """
        super().__init__(api_key, base_url)
        logger.info("KamisPriceAdapter 초기화 완료")
    
    def get_category(self) -> DataCategory:
        """데이터 카테고리 반환
        
        Returns:
            DataCategory.PRICE
        """
        return DataCategory.PRICE
    
    def fetch_data(
        self,
        date: Optional[datetime] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """도매시장 경락가격 데이터 수집
        
        Args:
            date: 수집할 날짜 (기본값: 오늘)
            **kwargs: 추가 파라미터
                - market_codes: 시장 코드 리스트 (선택적)
                - item_codes: 품목 코드 리스트 (선택적)
        
        Returns:
            List[Dict[str, Any]]: 수집된 가격 데이터
        """
        if date is None:
            date = datetime.now()
        
        target_date = date.strftime("%Y-%m-%d")
        
        logger.info(f"KAMIS 가격 데이터 수집 시작: {target_date}")
        
        try:
            # API 요청 파라미터
            params = {
                'p_yyyy': date.strftime("%Y"),
                'p_period': '1',  # 일별
                'p_returntype': 'json',
                'p_productclscode': self.SEAFOOD_CATEGORY,
                'p_regday': target_date,
            }
            
            # 시장 코드가 지정된 경우
            market_codes = kwargs.get('market_codes')
            if market_codes:
                params['p_countycode'] = ','.join(market_codes)
            
            # 품목 코드가 지정된 경우
            item_codes = kwargs.get('item_codes')
            if item_codes:
                params['p_itemcategorycode'] = ','.join(item_codes)
            
            # API 호출
            response = self.make_request(self.ENDPOINT, params)
            
            # 응답 파싱
            parsed_data = self.parse_response(response)
            
            logger.info(
                f"KAMIS 가격 데이터 수집 완료: {len(parsed_data)}건",
                extra={'date': target_date, 'count': len(parsed_data)}
            )
            
            return parsed_data
            
        except Exception as e:
            logger.error(
                f"KAMIS 가격 데이터 수집 실패: {e}",
                extra={'date': target_date, 'error': str(e)}
            )
            raise
    
    def parse_response(self, response: Dict) -> List[Dict[str, Any]]:
        """KAMIS API 응답 파싱
        
        KAMIS API 응답 구조:
        {
            "data": [
                {
                    "item_name": "광어(활)",
                    "item_code": "214",
                    "kind_name": "1kg",
                    "rank": "상",
                    "unit": "1kg",
                    "day1": "15000",
                    "dpr1": "0",
                    "countyname": "노량진수산",
                    "countycode": "1101",
                    "regday": "2024-01-15"
                },
                ...
            ]
        }
        
        Args:
            response: API 응답 딕셔너리
        
        Returns:
            List[Dict[str, Any]]: 파싱된 데이터 리스트
        """
        parsed_data = []
        
        try:
            # 응답 데이터 추출
            data_list = response.get('data', [])
            
            if not data_list:
                logger.warning("KAMIS API 응답에 데이터가 없습니다")
                return parsed_data
            
            for item in data_list:
                try:
                    # 필수 필드 확인
                    if not self._validate_item(item):
                        continue
                    
                    # 가격 추출 (day1 필드)
                    price_str = item.get('day1', '0')
                    price = self._parse_price(price_str)
                    
                    if price <= 0:
                        logger.debug(
                            f"가격이 0 이하: {item.get('item_name')} = {price}"
                        )
                        continue
                    
                    # 데이터 변환
                    parsed_item = {
                        'raw_name': item.get('item_name', '').strip(),
                        'item_code': item.get('item_code', ''),
                        'kind_name': item.get('kind_name', '').strip(),
                        'rank': item.get('rank', '').strip(),
                        'unit': self._normalize_unit(item.get('unit', 'kg')),
                        'price': price,
                        'market_name': item.get('countyname', '').strip(),
                        'market_code': item.get('countycode', ''),
                        'date': item.get('regday', ''),
                        'origin': '',  # KAMIS API는 원산지 정보 미제공
                        'source': 'KAMIS',
                    }
                    
                    parsed_data.append(parsed_item)
                    
                except Exception as e:
                    logger.warning(
                        f"항목 파싱 실패: {e}",
                        extra={'item': item, 'error': str(e)}
                    )
                    continue
            
            logger.info(f"KAMIS 응답 파싱 완료: {len(parsed_data)}건")
            
        except Exception as e:
            logger.error(
                f"KAMIS 응답 파싱 중 오류: {e}",
                extra={'error': str(e)}
            )
            raise
        
        return parsed_data
    
    def _validate_item(self, item: Dict) -> bool:
        """항목 유효성 검증
        
        Args:
            item: 검증할 항목
        
        Returns:
            bool: 유효 여부
        """
        # 필수 필드 확인
        required_fields = ['item_name', 'day1', 'countyname', 'regday']
        
        for field in required_fields:
            if field not in item or not item[field]:
                logger.debug(f"필수 필드 누락: {field}")
                return False
        
        # 품목명 검증
        item_name = item.get('item_name', '').strip()
        if len(item_name) < 2:
            logger.debug(f"품목명이 너무 짧음: {item_name}")
            return False
        
        return True
    
    def _parse_price(self, price_str: str) -> float:
        """가격 문자열을 float로 변환
        
        Args:
            price_str: 가격 문자열 (예: "15000", "15,000")
        
        Returns:
            float: 변환된 가격
        """
        try:
            # 쉼표 제거
            price_str = price_str.replace(',', '').strip()
            
            # 빈 문자열 처리
            if not price_str or price_str == '-':
                return 0.0
            
            # float 변환
            price = float(price_str)
            
            # 음수 처리
            if price < 0:
                return 0.0
            
            return price
            
        except (ValueError, AttributeError) as e:
            logger.debug(f"가격 파싱 실패: {price_str} - {e}")
            return 0.0
    
    def _normalize_unit(self, unit: str) -> str:
        """단위 표준화
        
        Args:
            unit: 원본 단위
        
        Returns:
            str: 표준화된 단위
        """
        if not unit:
            return 'kg'
        
        unit_lower = unit.lower().strip()
        
        # 단위 매핑
        unit_map = {
            'kg': 'kg',
            '1kg': 'kg',
            'kilogram': 'kg',
            '킬로그램': 'kg',
            '킬로': 'kg',
            '마리': '마리',
            '1마리': '마리',
            'ea': '마리',
            '개': '마리',
            '상자': '상자',
            '1상자': '상자',
            'box': '상자',
        }
        
        # 숫자 제거 (예: "10kg" -> "kg")
        import re
        unit_clean = re.sub(r'\d+', '', unit_lower).strip()
        
        normalized = unit_map.get(unit_clean, unit_map.get(unit_lower, 'kg'))
        
        return normalized
    
    def get_market_mapping(self) -> Dict[str, int]:
        """KAMIS 시장 코드를 내부 market_id로 매핑
        
        Returns:
            Dict[str, int]: {KAMIS 시장코드: 내부 market_id}
        """
        # TODO: 실제 DB의 markets 테이블과 매핑 필요
        # 현재는 하드코딩된 매핑 사용
        return {
            '1101': 1,  # 노량진수산 -> market_id 1
            '1102': 2,  # 가락시장 -> market_id 2
            # 추가 시장 매핑...
        }
    
    def convert_to_daily_prices(
        self,
        parsed_data: List[Dict[str, Any]],
        item_id_map: Dict[str, int]
    ) -> List[DailyPrice]:
        """파싱된 데이터를 DailyPrice 모델로 변환
        
        Args:
            parsed_data: 파싱된 데이터 리스트
            item_id_map: {품목명: item_id} 매핑
        
        Returns:
            List[DailyPrice]: DailyPrice 객체 리스트
        """
        daily_prices = []
        market_mapping = self.get_market_mapping()
        
        for data in parsed_data:
            try:
                # 품목 ID 매핑
                raw_name = data['raw_name']
                item_id = item_id_map.get(raw_name)
                
                if item_id is None:
                    logger.debug(f"품목 매핑 실패: {raw_name}")
                    continue
                
                # 시장 ID 매핑
                market_code = data['market_code']
                market_id = market_mapping.get(market_code)
                
                if market_id is None:
                    logger.debug(f"시장 매핑 실패: {market_code}")
                    continue
                
                # 날짜 변환
                date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
                
                # DailyPrice 객체 생성
                daily_price = DailyPrice(
                    item_id=item_id,
                    market_id=market_id,
                    price=data['price'],
                    unit=data['unit'],
                    origin=data['origin'],
                    date=date_obj,
                    quantity=None,
                    source=data['source']
                )
                
                daily_prices.append(daily_price)
                
            except Exception as e:
                logger.warning(
                    f"DailyPrice 변환 실패: {e}",
                    extra={'data': data, 'error': str(e)}
                )
                continue
        
        logger.info(f"DailyPrice 변환 완료: {len(daily_prices)}건")
        
        return daily_prices
