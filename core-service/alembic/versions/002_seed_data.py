"""Seed initial data

Revision ID: 002
Revises: 001
Create Date: 2025-11-10 10:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """초기 데이터 삽입"""
    
    # 시장 데이터
    markets_table = table(
        'markets',
        column('id', sa.Integer),
        column('name', sa.String),
        column('code', sa.String),
        column('type', sa.String)
    )
    
    op.bulk_insert(
        markets_table,
        [
            {'id': 1, 'name': '가락시장', 'code': 'GARAK', 'type': 'wholesale'},
            {'id': 2, 'name': '노량진수산시장', 'code': 'NORYANGJIN', 'type': 'retail'},
        ]
    )
    
    # 품목 데이터 (주요 수산물)
    items_table = table(
        'items',
        column('id', sa.Integer),
        column('name_ko', sa.String),
        column('name_en', sa.String),
        column('category', sa.String),
        column('season_start', sa.Integer),
        column('season_end', sa.Integer),
        column('default_origin', sa.String),
        column('unit_default', sa.String)
    )
    
    op.bulk_insert(
        items_table,
        [
            # 생선류
            {'id': 1, 'name_ko': '광어', 'name_en': 'Flounder', 'category': 'fish', 
             'season_start': 11, 'season_end': 2, 'default_origin': '제주', 'unit_default': 'kg'},
            {'id': 2, 'name_ko': '고등어', 'name_en': 'Mackerel', 'category': 'fish', 
             'season_start': 9, 'season_end': 12, 'default_origin': '부산', 'unit_default': 'kg'},
            {'id': 3, 'name_ko': '갈치', 'name_en': 'Hairtail', 'category': 'fish', 
             'season_start': 8, 'season_end': 11, 'default_origin': '제주', 'unit_default': 'kg'},
            {'id': 4, 'name_ko': '삼치', 'name_en': 'Spanish Mackerel', 'category': 'fish', 
             'season_start': 10, 'season_end': 12, 'default_origin': '남해', 'unit_default': 'kg'},
            {'id': 5, 'name_ko': '조기', 'name_en': 'Yellow Croaker', 'category': 'fish', 
             'season_start': 4, 'season_end': 6, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 6, 'name_ko': '명태', 'name_en': 'Alaska Pollock', 'category': 'fish', 
             'season_start': 12, 'season_end': 2, 'default_origin': '동해', 'unit_default': 'kg'},
            {'id': 7, 'name_ko': '오징어', 'name_en': 'Squid', 'category': 'fish', 
             'season_start': 6, 'season_end': 9, 'default_origin': '동해', 'unit_default': 'kg'},
            {'id': 8, 'name_ko': '꽁치', 'name_en': 'Pacific Saury', 'category': 'fish', 
             'season_start': 9, 'season_end': 11, 'default_origin': '동해', 'unit_default': 'kg'},
            
            # 조개류
            {'id': 9, 'name_ko': '굴', 'name_en': 'Oyster', 'category': 'shellfish', 
             'season_start': 11, 'season_end': 3, 'default_origin': '통영', 'unit_default': 'kg'},
            {'id': 10, 'name_ko': '바지락', 'name_en': 'Manila Clam', 'category': 'shellfish', 
             'season_start': 3, 'season_end': 5, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 11, 'name_ko': '홍합', 'name_en': 'Mussel', 'category': 'shellfish', 
             'season_start': 12, 'season_end': 3, 'default_origin': '남해', 'unit_default': 'kg'},
            {'id': 12, 'name_ko': '전복', 'name_en': 'Abalone', 'category': 'shellfish', 
             'season_start': 6, 'season_end': 8, 'default_origin': '제주', 'unit_default': '마리'},
            
            # 갑각류
            {'id': 13, 'name_ko': '대게', 'name_en': 'Snow Crab', 'category': 'crustacean', 
             'season_start': 11, 'season_end': 5, 'default_origin': '동해', 'unit_default': 'kg'},
            {'id': 14, 'name_ko': '꽃게', 'name_en': 'Blue Crab', 'category': 'crustacean', 
             'season_start': 4, 'season_end': 6, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 15, 'name_ko': '새우', 'name_en': 'Shrimp', 'category': 'crustacean', 
             'season_start': 5, 'season_end': 9, 'default_origin': '서해', 'unit_default': 'kg'},
            
            # 기타
            {'id': 16, 'name_ko': '미역', 'name_en': 'Seaweed', 'category': 'other', 
             'season_start': 2, 'season_end': 4, 'default_origin': '완도', 'unit_default': 'kg'},
            {'id': 17, 'name_ko': '김', 'name_en': 'Laver', 'category': 'other', 
             'season_start': 11, 'season_end': 2, 'default_origin': '완도', 'unit_default': '상자'},
            {'id': 18, 'name_ko': '멍게', 'name_en': 'Sea Squirt', 'category': 'other', 
             'season_start': 5, 'season_end': 7, 'default_origin': '통영', 'unit_default': 'kg'},
        ]
    )
    
    # 품목 별칭 데이터 (예시)
    aliases_table = table(
        'item_aliases',
        column('item_id', sa.Integer),
        column('market_id', sa.Integer),
        column('raw_name', sa.String),
        column('confidence', sa.DECIMAL)
    )
    
    op.bulk_insert(
        aliases_table,
        [
            # 광어 별칭
            {'item_id': 1, 'market_id': 1, 'raw_name': '광어(대)', 'confidence': 1.0},
            {'item_id': 1, 'market_id': 1, 'raw_name': '광어(중)', 'confidence': 1.0},
            {'item_id': 1, 'market_id': 2, 'raw_name': '광어', 'confidence': 1.0},
            {'item_id': 1, 'market_id': 2, 'raw_name': '넙치', 'confidence': 1.0},
            
            # 고등어 별칭
            {'item_id': 2, 'market_id': 1, 'raw_name': '고등어', 'confidence': 1.0},
            {'item_id': 2, 'market_id': 2, 'raw_name': '고등어(국산)', 'confidence': 1.0},
            {'item_id': 2, 'market_id': 2, 'raw_name': '고등어(노르웨이)', 'confidence': 1.0},
            
            # 갈치 별칭
            {'item_id': 3, 'market_id': 1, 'raw_name': '갈치', 'confidence': 1.0},
            {'item_id': 3, 'market_id': 2, 'raw_name': '갈치(제주)', 'confidence': 1.0},
            
            # 오징어 별칭
            {'item_id': 7, 'market_id': 1, 'raw_name': '오징어', 'confidence': 1.0},
            {'item_id': 7, 'market_id': 2, 'raw_name': '오징어(국산)', 'confidence': 1.0},
            {'item_id': 7, 'market_id': 2, 'raw_name': '생물오징어', 'confidence': 1.0},
        ]
    )


def downgrade() -> None:
    """초기 데이터 삭제"""
    op.execute("DELETE FROM item_aliases")
    op.execute("DELETE FROM items")
    op.execute("DELETE FROM markets")
