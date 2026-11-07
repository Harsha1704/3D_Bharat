"""add_heritage_sources_media_and_3d_assets

Revision ID: eab84cd87dd6
Revises: e088d3687b98
Create Date: 2026-11-07 13:49:22.108917
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = 'eab84cd87dd6'
down_revision: Union[str, Sequence[str], None] = 'e088d3687b98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================
    # 1. HERITAGE SOURCES TABLE
    # =========================================================
    op.create_table(
        'heritage_sources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('heritage_site_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=100), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('institution', sa.String(length=255), nullable=True),
        sa.Column('publication_date', sa.String(length=100), nullable=True),
        sa.Column('citation', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), server_default='UNVERIFIED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['heritage_site_id'], ['heritage_sites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_heritage_sources_heritage_site_id'), 'heritage_sources', ['heritage_site_id'], unique=False)
    op.create_index(op.f('ix_heritage_sources_title'), 'heritage_sources', ['title'], unique=False)
    op.create_index(op.f('ix_heritage_sources_source_type'), 'heritage_sources', ['source_type'], unique=False)
    op.create_index(op.f('ix_heritage_sources_verification_status'), 'heritage_sources', ['verification_status'], unique=False)

    # =========================================================
    # 2. HERITAGE MEDIA TABLE
    # =========================================================
    op.create_table(
        'heritage_media',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('heritage_site_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=False),
        sa.Column('storage_key', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
        sa.Column('attribution', sa.String(length=255), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('capture_date', sa.String(length=100), nullable=True),
        sa.Column('verification_status', sa.String(length=50), server_default='UNVERIFIED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['heritage_site_id'], ['heritage_sites.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['heritage_sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_heritage_media_heritage_site_id'), 'heritage_media', ['heritage_site_id'], unique=False)
    op.create_index(op.f('ix_heritage_media_source_id'), 'heritage_media', ['source_id'], unique=False)
    op.create_index(op.f('ix_heritage_media_title'), 'heritage_media', ['title'], unique=False)
    op.create_index(op.f('ix_heritage_media_media_type'), 'heritage_media', ['media_type'], unique=False)
    op.create_index(op.f('ix_heritage_media_storage_key'), 'heritage_media', ['storage_key'], unique=True)
    op.create_index(op.f('ix_heritage_media_checksum_sha256'), 'heritage_media', ['checksum_sha256'], unique=False)
    op.create_index(op.f('ix_heritage_media_verification_status'), 'heritage_media', ['verification_status'], unique=False)

    # =========================================================
    # 3. HERITAGE 3D ASSETS TABLE
    # =========================================================
    op.create_table(
        'heritage_3d_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('heritage_site_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_format', sa.String(length=50), nullable=False),
        sa.Column('storage_key', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
        sa.Column('units', sa.String(length=50), server_default='meters', nullable=True),
        sa.Column('coordinate_system', sa.String(length=100), nullable=True),
        sa.Column('companion_files', ARRAY(sa.String()), nullable=True),
        sa.Column('bounding_box', sa.Text(), nullable=True),
        sa.Column('attribution', sa.String(length=255), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('processing_status', sa.String(length=50), server_default='READY', nullable=False),
        sa.Column('verification_status', sa.String(length=50), server_default='UNVERIFIED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['heritage_site_id'], ['heritage_sites.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['heritage_sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_heritage_3d_assets_heritage_site_id'), 'heritage_3d_assets', ['heritage_site_id'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_source_id'), 'heritage_3d_assets', ['source_id'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_title'), 'heritage_3d_assets', ['title'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_asset_format'), 'heritage_3d_assets', ['asset_format'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_storage_key'), 'heritage_3d_assets', ['storage_key'], unique=True)
    op.create_index(op.f('ix_heritage_3d_assets_checksum_sha256'), 'heritage_3d_assets', ['checksum_sha256'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_processing_status'), 'heritage_3d_assets', ['processing_status'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_verification_status'), 'heritage_3d_assets', ['verification_status'], unique=False)

    # =========================================================
    # 4. DATABASE CHECK CONSTRAINTS
    # =========================================================
    op.create_check_constraint(
        'ck_heritage_sites_lat',
        'heritage_sites',
        'latitude IS NULL OR (latitude >= -90.0 AND latitude <= 90.0)'
    )
    op.create_check_constraint(
        'ck_heritage_sites_lon',
        'heritage_sites',
        'longitude IS NULL OR (longitude >= -180.0 AND longitude <= 180.0)'
    )
    op.create_check_constraint(
        'ck_heritage_connections_conf',
        'heritage_connections',
        'confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)'
    )
    op.create_check_constraint(
        'ck_heritage_connections_noself',
        'heritage_connections',
        'source_site_id != target_site_id'
    )


def downgrade() -> None:
    # Drop check constraints
    op.drop_constraint('ck_heritage_connections_noself', 'heritage_connections', type_='check')
    op.drop_constraint('ck_heritage_connections_conf', 'heritage_connections', type_='check')
    op.drop_constraint('ck_heritage_sites_lon', 'heritage_sites', type_='check')
    op.drop_constraint('ck_heritage_sites_lat', 'heritage_sites', type_='check')

    # Drop 3D assets
    op.drop_index(op.f('ix_heritage_3d_assets_verification_status'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_processing_status'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_checksum_sha256'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_storage_key'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_asset_format'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_title'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_source_id'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_heritage_site_id'), table_name='heritage_3d_assets')
    op.drop_table('heritage_3d_assets')

    # Drop media
    op.drop_index(op.f('ix_heritage_media_verification_status'), table_name='heritage_media')
    op.drop_index(op.f('ix_heritage_media_checksum_sha256'), table_name='heritage_media')
    op.drop_index(op.f('ix_heritage_media_storage_key'), table_name='heritage_media')
    op.drop_index(op.f('ix_heritage_media_media_type'), table_name='heritage_media')
    op.drop_index(op.f('ix_heritage_media_title'), table_name='heritage_media')
    op.drop_index(op.f('ix_heritage_media_source_id'), table_name='heritage_media')
    op.drop_index(op.f('ix_heritage_media_heritage_site_id'), table_name='heritage_media')
    op.drop_table('heritage_media')

    # Drop sources
    op.drop_index(op.f('ix_heritage_sources_verification_status'), table_name='heritage_sources')
    op.drop_index(op.f('ix_heritage_sources_source_type'), table_name='heritage_sources')
    op.drop_index(op.f('ix_heritage_sources_title'), table_name='heritage_sources')
    op.drop_index(op.f('ix_heritage_sources_heritage_site_id'), table_name='heritage_sources')
    op.drop_table('heritage_sources')
