"""공공데이터 API 통합 스키마

Revision ID: 003
Revises: 002
Create Date: 2025-11-11 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """공공데이터 API 통합을 위한 테이블 생성"""
    
    # 1. species_codes 테이블 - 어종 코드
    op.create_table(
        'species_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name_ko', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_species_codes_id'), 'species_codes', ['id'], unique=False)
    op.create_index(op.f('ix_species_codes_code'), 'species_codes', ['code'], unique=False)
    op.create_index(op.f('ix_species_codes_name_ko'), 'species_codes', ['name_ko'], unique=False)
    
    # 2. traceability_codes 테이블 - 수산물이력제 품목코드
    op.create_table(
        'traceability_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('product_name', sa.String(length=100), nullable=False),
        sa.Column('registration_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_traceability_codes_id'), 'traceability_codes', ['id'], unique=False)
    op.create_index(op.f('ix_traceability_codes_code'), 'traceability_codes', ['code'], unique=False)
    op.create_index(op.f('ix_traceability_codes_product_name'), 'traceability_codes', ['product_name'], unique=False)
    
    # 3. certifications 테이블 - 인증 정보
    op.create_table(
        'certifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cert_type', sa.String(length=20), nullable=False),
        sa.Column('product_name', sa.String(length=100), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=True),
        sa.Column('cert_number', sa.String(length=100), nullable=True),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_until', sa.Date(), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('item_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cert_number')
    )
    op.create_index(op.f('ix_certifications_id'), 'certifications', ['id'], unique=False)
    op.create_index(op.f('ix_certifications_item_id'), 'certifications', ['item_id'], unique=False)
    op.create_index(op.f('ix_certifications_is_active'), 'certifications', ['is_active'], unique=False)
    op.create_index(op.f('ix_certifications_cert_type'), 'certifications', ['cert_type'], unique=False)
    op.create_index('idx_certifications_product_name', 'certifications', ['product_name'], unique=False)

    # 4. prohibited_species 테이블 - 포획 금지 어종
    op.create_table(
        'prohibited_species',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('species_code', sa.String(length=50), nullable=False),
        sa.Column('name_ko', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=True),
        sa.Column('prohibition_start', sa.Date(), nullable=False),
        sa.Column('prohibition_end', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prohibited_species_id'), 'prohibited_species', ['id'], unique=False)
    op.create_index(op.f('ix_prohibited_species_species_code'), 'prohibited_species', ['species_code'], unique=False)
    op.create_index(op.f('ix_prohibited_species_name_ko'), 'prohibited_species', ['name_ko'], unique=False)
    
    # 5. distribution_stats 테이블 - 유통 통계
    op.create_table(
        'distribution_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('auction_location', sa.String(length=100), nullable=False),
        sa.Column('origin', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('amount', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'auction_location', 'date', name='uq_item_auction_date')
    )
    op.create_index(op.f('ix_distribution_stats_id'), 'distribution_stats', ['id'], unique=False)
    op.create_index(op.f('ix_distribution_stats_item_id'), 'distribution_stats', ['item_id'], unique=False)
    op.create_index('idx_distribution_date', 'distribution_stats', ['date'], unique=False)
    op.create_index('idx_distribution_item_date', 'distribution_stats', ['item_id', 'date'], unique=False)
    
    # 6. monthly_prices 테이블 - 월별 가격
    op.create_table(
        'monthly_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('avg_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('min_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('max_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'year', 'month', name='uq_item_year_month')
    )
    op.create_index(op.f('ix_monthly_prices_id'), 'monthly_prices', ['id'], unique=False)
    op.create_index(op.f('ix_monthly_prices_item_id'), 'monthly_prices', ['item_id'], unique=False)
    op.create_index('idx_monthly_prices_period', 'monthly_prices', ['year', 'month'], unique=False)
    op.create_index('idx_monthly_prices_item_period', 'monthly_prices', ['item_id', 'year', 'month'], unique=False)


def downgrade() -> None:
    """테이블 삭제"""
    
    # monthly_prices 테이블 삭제
    op.drop_index('idx_monthly_prices_item_period', table_name='monthly_prices')
    op.drop_index('idx_monthly_prices_period', table_name='monthly_prices')
    op.drop_index(op.f('ix_monthly_prices_item_id'), table_name='monthly_prices')
    op.drop_index(op.f('ix_monthly_prices_id'), table_name='monthly_prices')
    op.drop_table('monthly_prices')
    
    # distribution_stats 테이블 삭제
    op.drop_index('idx_distribution_item_date', table_name='distribution_stats')
    op.drop_index('idx_distribution_date', table_name='distribution_stats')
    op.drop_index(op.f('ix_distribution_stats_item_id'), table_name='distribution_stats')
    op.drop_index(op.f('ix_distribution_stats_id'), table_name='distribution_stats')
    op.drop_table('distribution_stats')
    
    # prohibited_species 테이블 삭제
    op.drop_index(op.f('ix_prohibited_species_name_ko'), table_name='prohibited_species')
    op.drop_index(op.f('ix_prohibited_species_species_code'), table_name='prohibited_species')
    op.drop_index(op.f('ix_prohibited_species_id'), table_name='prohibited_species')
    op.drop_table('prohibited_species')
    
    # certifications 테이블 삭제
    op.drop_index('idx_certifications_product_name', table_name='certifications')
    op.drop_index(op.f('ix_certifications_cert_type'), table_name='certifications')
    op.drop_index(op.f('ix_certifications_is_active'), table_name='certifications')
    op.drop_index(op.f('ix_certifications_item_id'), table_name='certifications')
    op.drop_index(op.f('ix_certifications_id'), table_name='certifications')
    op.drop_table('certifications')
    
    # traceability_codes 테이블 삭제
    op.drop_index(op.f('ix_traceability_codes_product_name'), table_name='traceability_codes')
    op.drop_index(op.f('ix_traceability_codes_code'), table_name='traceability_codes')
    op.drop_index(op.f('ix_traceability_codes_id'), table_name='traceability_codes')
    op.drop_table('traceability_codes')
    
    # species_codes 테이블 삭제
    op.drop_index(op.f('ix_species_codes_name_ko'), table_name='species_codes')
    op.drop_index(op.f('ix_species_codes_code'), table_name='species_codes')
    op.drop_index(op.f('ix_species_codes_id'), table_name='species_codes')
    op.drop_table('species_codes')
