"""add_import_batches_and_monument_provenance

Revision ID: c4d9a2b71e8f
Revises: eab84cd87dd6
Create Date: 2026-11-07 14:33:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4d9a2b71e8f'
down_revision: Union[str, None] = 'eab84cd87dd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. CREATE TABLE import_batches
    # ---------------------------------------------------------
    op.create_table(
        'import_batches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_id', sa.String(length=100), nullable=False),
        sa.Column('source_organization', sa.String(length=200), nullable=False),
        sa.Column('source_dataset', sa.String(length=200), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('total_records', sa.Integer(), server_default='0', nullable=False),
        sa.Column('accepted_records', sa.Integer(), server_default='0', nullable=False),
        sa.Column('rejected_records', sa.Integer(), server_default='0', nullable=False),
        sa.Column('duplicate_records', sa.Integer(), server_default='0', nullable=False),
        sa.Column('updated_records', sa.Integer(), server_default='0', nullable=False),
        sa.Column('inserted_records', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_id')
    )
    op.create_index(op.f('ix_import_batches_batch_id'), 'import_batches', ['batch_id'], unique=True)
    op.create_index(op.f('ix_import_batches_source_organization'), 'import_batches', ['source_organization'], unique=False)
    op.create_index(op.f('ix_import_batches_source_dataset'), 'import_batches', ['source_dataset'], unique=False)
    op.create_index(op.f('ix_import_batches_status'), 'import_batches', ['status'], unique=False)

    # ---------------------------------------------------------
    # 2. ADD COLUMNS TO heritage_sites
    # ---------------------------------------------------------
    op.add_column('heritage_sites', sa.Column('alternative_names', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('heritage_sites', sa.Column('dynasty', sa.String(length=100), nullable=True))
    op.add_column('heritage_sites', sa.Column('construction_year', sa.String(length=100), nullable=True))
    op.add_column('heritage_sites', sa.Column('verification_status', sa.String(length=50), server_default='OFFICIAL_SOURCE', nullable=False))
    op.add_column('heritage_sites', sa.Column('batch_id', sa.String(length=100), nullable=True))
    op.add_column('heritage_sites', sa.Column('source_reference', sa.String(length=255), nullable=True))
    op.add_column('heritage_sites', sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True))

    # ---------------------------------------------------------
    # 3. ADD PERFORMANCE & COMPOSITE INDEXES TO heritage_sites
    # ---------------------------------------------------------
    op.create_index(op.f('ix_heritage_sites_dynasty'), 'heritage_sites', ['dynasty'], unique=False)
    op.create_index(op.f('ix_heritage_sites_verification_status'), 'heritage_sites', ['verification_status'], unique=False)
    op.create_index(op.f('ix_heritage_sites_batch_id'), 'heritage_sites', ['batch_id'], unique=False)
    op.create_index('ix_heritage_sites_district', 'heritage_sites', ['district'], unique=False)
    op.create_index('ix_heritage_sites_lat_lon', 'heritage_sites', ['latitude', 'longitude'], unique=False)
    op.create_index('ix_heritage_sites_state_category', 'heritage_sites', ['state', 'category'], unique=False)


def downgrade() -> None:
    # ---------------------------------------------------------
    # 1. DROP INDEXES AND COLUMNS ON heritage_sites
    # ---------------------------------------------------------
    op.drop_index('ix_heritage_sites_state_category', table_name='heritage_sites')
    op.drop_index('ix_heritage_sites_lat_lon', table_name='heritage_sites')
    op.drop_index('ix_heritage_sites_district', table_name='heritage_sites')
    op.drop_index(op.f('ix_heritage_sites_batch_id'), table_name='heritage_sites')
    op.drop_index(op.f('ix_heritage_sites_verification_status'), table_name='heritage_sites')
    op.drop_index(op.f('ix_heritage_sites_dynasty'), table_name='heritage_sites')

    op.drop_column('heritage_sites', 'last_verified_at')
    op.drop_column('heritage_sites', 'source_reference')
    op.drop_column('heritage_sites', 'batch_id')
    op.drop_column('heritage_sites', 'verification_status')
    op.drop_column('heritage_sites', 'construction_year')
    op.drop_column('heritage_sites', 'dynasty')
    op.drop_column('heritage_sites', 'alternative_names')

    # ---------------------------------------------------------
    # 2. DROP import_batches TABLE
    # ---------------------------------------------------------
    op.drop_index(op.f('ix_import_batches_status'), table_name='import_batches')
    op.drop_index(op.f('ix_import_batches_source_dataset'), table_name='import_batches')
    op.drop_index(op.f('ix_import_batches_source_organization'), table_name='import_batches')
    op.drop_index(op.f('ix_import_batches_batch_id'), table_name='import_batches')
    op.drop_table('import_batches')
