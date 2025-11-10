"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-11-10 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """테이블 생성"""
    
    # items 테이블
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name_ko', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('season_start', sa.Integer(), nullable=True),
        sa.Column('season_end', sa.Integer(), nullable=True),
        sa.Column('default_origin', sa.String(length=100), nullable=True),
        sa.Column('unit_default', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_name_ko'), 'items', ['name_ko'], unique=False)
    op.create_index(op.f('ix_items_category'), 'items', ['category'], unique=False)
    
    # markets 테이블
    op.create_table(
        'markets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_markets_id'), 'markets', ['id'], unique=False)
    op.create_index(op.f('ix_markets_code'), 'markets', ['code'], unique=False)
    
    # market_prices 테이블
    op.create_table(
        'market_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('market_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('origin', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'market_id', 'date', name='uq_item_market_date')
    )
    op.create_index(op.f('ix_market_prices_id'), 'market_prices', ['id'], unique=False)
    op.create_index('idx_market_prices_item_date', 'market_prices', ['item_id', 'date'], unique=False)
    op.create_index('idx_market_prices_market_date', 'market_prices', ['market_id', 'date'], unique=False)
    
    # price_rules 테이블
    op.create_table(
        'price_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('high_threshold', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('low_threshold', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('min_days', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id')
    )
    op.create_index(op.f('ix_price_rules_id'), 'price_rules', ['id'], unique=False)
    
    # item_aliases 테이블
    op.create_table(
        'item_aliases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('market_id', sa.Integer(), nullable=False),
        sa.Column('raw_name', sa.String(length=200), nullable=False),
        sa.Column('confidence', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('market_id', 'raw_name', name='uq_market_raw_name')
    )
    op.create_index(op.f('ix_item_aliases_id'), 'item_aliases', ['id'], unique=False)
    op.create_index(op.f('ix_item_aliases_raw_name'), 'item_aliases', ['raw_name'], unique=False)


def downgrade() -> None:
    """테이블 삭제"""
    op.drop_index(op.f('ix_item_aliases_raw_name'), table_name='item_aliases')
    op.drop_index(op.f('ix_item_aliases_id'), table_name='item_aliases')
    op.drop_table('item_aliases')
    
    op.drop_index(op.f('ix_price_rules_id'), table_name='price_rules')
    op.drop_table('price_rules')
    
    op.drop_index('idx_market_prices_market_date', table_name='market_prices')
    op.drop_index('idx_market_prices_item_date', table_name='market_prices')
    op.drop_index(op.f('ix_market_prices_id'), table_name='market_prices')
    op.drop_table('market_prices')
    
    op.drop_index(op.f('ix_markets_code'), table_name='markets')
    op.drop_index(op.f('ix_markets_id'), table_name='markets')
    op.drop_table('markets')
    
    op.drop_index(op.f('ix_items_category'), table_name='items')
    op.drop_index(op.f('ix_items_name_ko'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items')
