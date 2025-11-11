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
            # 주요 어류
            {'id': 1, 'name_ko': '광어', 'name_en': 'Flounder', 'category': 'fish',
             'season_start': 11, 'season_end': 2, 'default_origin': '제주', 'unit_default': 'kg'},
            {'id': 2, 'name_ko': '우럭', 'name_en': 'Rockfish', 'category': 'fish',
             'season_start': 3, 'season_end': 6, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 3, 'name_ko': '참돔', 'name_en': 'Red Seabream', 'category': 'fish',
             'season_start': 4, 'season_end': 6, 'default_origin': '남해', 'unit_default': 'kg'},
            {'id': 4, 'name_ko': '연어', 'name_en': 'Salmon', 'category': 'fish',
             'season_start': 9, 'season_end': 11, 'default_origin': '노르웨이', 'unit_default': 'kg'},
            {'id': 5, 'name_ko': '돌돔', 'name_en': 'Striped Beakfish', 'category': 'fish',
             'season_start': 6, 'season_end': 8, 'default_origin': '제주', 'unit_default': 'kg'},
            {'id': 6, 'name_ko': '감성돔', 'name_en': 'Black Porgy', 'category': 'fish',
             'season_start': 10, 'season_end': 12, 'default_origin': '남해', 'unit_default': 'kg'},
            {'id': 7, 'name_ko': '방어', 'name_en': 'Yellowtail Amberjack', 'category': 'fish',
             'season_start': 11, 'season_end': 2, 'default_origin': '제주', 'unit_default': 'kg'},
            {'id': 8, 'name_ko': '민어', 'name_en': 'Croaker', 'category': 'fish',
             'season_start': 6, 'season_end': 8, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 9, 'name_ko': '농어', 'name_en': 'Sea Bass', 'category': 'fish',
             'season_start': 5, 'season_end': 7, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 10, 'name_ko': '고등어', 'name_en': 'Mackerel', 'category': 'fish',
             'season_start': 9, 'season_end': 12, 'default_origin': '동해', 'unit_default': 'kg'},

            # 갑각류 및 패류
            {'id': 11, 'name_ko': '대게', 'name_en': 'Snow Crab', 'category': 'crustacean',
             'season_start': 11, 'season_end': 4, 'default_origin': '동해', 'unit_default': 'kg'},
            {'id': 12, 'name_ko': '킹크랩', 'name_en': 'King Crab', 'category': 'crustacean',
             'season_start': 11, 'season_end': 3, 'default_origin': '러시아', 'unit_default': 'kg'},
            {'id': 13, 'name_ko': '코끼리조개', 'name_en': 'Geoduck', 'category': 'shellfish',
             'season_start': 3, 'season_end': 5, 'default_origin': '전남', 'unit_default': 'kg'},
            {'id': 14, 'name_ko': '왕우럭조개', 'name_en': 'King Turban Shell', 'category': 'shellfish',
             'season_start': 5, 'season_end': 8, 'default_origin': '제주', 'unit_default': 'kg'},
            {'id': 15, 'name_ko': '전복', 'name_en': 'Abalone', 'category': 'shellfish',
             'season_start': 6, 'season_end': 9, 'default_origin': '완도', 'unit_default': '마리'},
            {'id': 16, 'name_ko': '참소라', 'name_en': 'Top Shell', 'category': 'shellfish',
             'season_start': 7, 'season_end': 9, 'default_origin': '제주', 'unit_default': 'kg'},

            # 기타 해산물
            {'id': 17, 'name_ko': '멍게', 'name_en': 'Sea Squirt', 'category': 'other',
             'season_start': 4, 'season_end': 6, 'default_origin': '통영', 'unit_default': 'kg'},
            {'id': 18, 'name_ko': '해삼', 'name_en': 'Sea Cucumber', 'category': 'other',
             'season_start': 12, 'season_end': 2, 'default_origin': '남해', 'unit_default': 'kg'},
            {'id': 19, 'name_ko': '개불', 'name_en': 'Spoon Worm', 'category': 'other',
             'season_start': 2, 'season_end': 4, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 20, 'name_ko': '낙지', 'name_en': 'Octopus', 'category': 'cephalopod',
             'season_start': 7, 'season_end': 10, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 21, 'name_ko': '새우', 'name_en': 'Shrimp', 'category': 'crustacean',
             'season_start': 5, 'season_end': 9, 'default_origin': '서해', 'unit_default': 'kg'},
            {'id': 22, 'name_ko': '갑오징어', 'name_en': 'Cuttlefish', 'category': 'cephalopod',
             'season_start': 4, 'season_end': 6, 'default_origin': '남해', 'unit_default': 'kg'},
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
            # 광어 및 주요 생선
            {'item_id': 1, 'market_id': 1, 'raw_name': '광어(대)', 'confidence': 1.0},
            {'item_id': 1, 'market_id': 2, 'raw_name': '넙치', 'confidence': 0.95},
            {'item_id': 2, 'market_id': 1, 'raw_name': '참우럭', 'confidence': 0.95},
            {'item_id': 2, 'market_id': 2, 'raw_name': '우럭', 'confidence': 1.0},
            {'item_id': 3, 'market_id': 1, 'raw_name': '참돔', 'confidence': 1.0},
            {'item_id': 4, 'market_id': 2, 'raw_name': '연어', 'confidence': 1.0},
            {'item_id': 5, 'market_id': 1, 'raw_name': '활돌돔', 'confidence': 1.0},
            {'item_id': 6, 'market_id': 2, 'raw_name': '감성돔', 'confidence': 1.0},
            {'item_id': 7, 'market_id': 1, 'raw_name': '방어', 'confidence': 1.0},
            {'item_id': 10, 'market_id': 2, 'raw_name': '고등어', 'confidence': 1.0},

            # 고가 해산물
            {'item_id': 11, 'market_id': 1, 'raw_name': '대게', 'confidence': 1.0},
            {'item_id': 12, 'market_id': 2, 'raw_name': '킹크랩', 'confidence': 1.0},
            {'item_id': 13, 'market_id': 1, 'raw_name': '코끼리조개', 'confidence': 1.0},
            {'item_id': 14, 'market_id': 2, 'raw_name': '왕우럭조개', 'confidence': 1.0},
            {'item_id': 15, 'market_id': 1, 'raw_name': '완도전복', 'confidence': 1.0},
            {'item_id': 16, 'market_id': 2, 'raw_name': '참소라', 'confidence': 1.0},

            # 기타
            {'item_id': 17, 'market_id': 2, 'raw_name': '멍게', 'confidence': 1.0},
            {'item_id': 18, 'market_id': 2, 'raw_name': '해삼', 'confidence': 1.0},
            {'item_id': 19, 'market_id': 2, 'raw_name': '개불', 'confidence': 1.0},
            {'item_id': 20, 'market_id': 1, 'raw_name': '생낙지', 'confidence': 1.0},
            {'item_id': 22, 'market_id': 1, 'raw_name': '갑오징어', 'confidence': 1.0},
        ]
    )


def downgrade() -> None:
    """초기 데이터 삭제"""
    op.execute("DELETE FROM item_aliases")
    op.execute("DELETE FROM items")
    op.execute("DELETE FROM markets")
