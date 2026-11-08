"""add_phase10_3d_pipeline_and_provenance

Revision ID: b4e9c8f2a103
Revises: a3f8b7c1d902
Create Date: 2026-11-07 23:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4e9c8f2a103'
down_revision: Union[str, None] = 'a3f8b7c1d902'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Add minimal additive provenance, technical, and validation
    # fields to heritage_3d_assets
    # ---------------------------------------------------------
    op.add_column(
        'heritage_3d_assets',
        sa.Column('asset_origin', sa.String(length=50), server_default='HISTORICAL_RECONSTRUCTION', nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('original_format', sa.String(length=50), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('processed_format', sa.String(length=50), server_default='GLB', nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('preview_image_key', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('source_url', sa.String(length=1000), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('source_identifier', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('creator', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('publisher', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('licence_name', sa.String(length=255), server_default='CC-BY-4.0', nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('licence_url', sa.String(length=1000), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('rights_status', sa.String(length=50), server_default='CREATIVE_COMMONS', nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('attribution_text', sa.Text(), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('commercial_use_allowed', sa.Boolean(), server_default=sa.false(), nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('modification_allowed', sa.Boolean(), server_default=sa.true(), nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('redistribution_allowed', sa.Boolean(), server_default=sa.true(), nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('poly_count', sa.Integer(), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('vertex_count', sa.Integer(), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('texture_resolution', sa.String(length=50), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('lod_levels', sa.Integer(), server_default='1', nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('coordinate_notes', sa.Text(), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('validation_status', sa.String(length=50), server_default='READY', nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('validation_report', sa.Text(), nullable=True)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('visibility_status', sa.String(length=50), server_default='PUBLIC', nullable=False)
    )
    op.add_column(
        'heritage_3d_assets',
        sa.Column('is_pilot', sa.Boolean(), server_default=sa.false(), nullable=False)
    )

    op.create_index(op.f('ix_heritage_3d_assets_asset_origin'), 'heritage_3d_assets', ['asset_origin'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_rights_status'), 'heritage_3d_assets', ['rights_status'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_validation_status'), 'heritage_3d_assets', ['validation_status'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_visibility_status'), 'heritage_3d_assets', ['visibility_status'], unique=False)
    op.create_index(op.f('ix_heritage_3d_assets_is_pilot'), 'heritage_3d_assets', ['is_pilot'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_heritage_3d_assets_is_pilot'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_visibility_status'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_validation_status'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_rights_status'), table_name='heritage_3d_assets')
    op.drop_index(op.f('ix_heritage_3d_assets_asset_origin'), table_name='heritage_3d_assets')

    op.drop_column('heritage_3d_assets', 'is_pilot')
    op.drop_column('heritage_3d_assets', 'visibility_status')
    op.drop_column('heritage_3d_assets', 'validation_report')
    op.drop_column('heritage_3d_assets', 'validation_status')
    op.drop_column('heritage_3d_assets', 'coordinate_notes')
    op.drop_column('heritage_3d_assets', 'lod_levels')
    op.drop_column('heritage_3d_assets', 'texture_resolution')
    op.drop_column('heritage_3d_assets', 'vertex_count')
    op.drop_column('heritage_3d_assets', 'poly_count')
    op.drop_column('heritage_3d_assets', 'redistribution_allowed')
    op.drop_column('heritage_3d_assets', 'modification_allowed')
    op.drop_column('heritage_3d_assets', 'commercial_use_allowed')
    op.drop_column('heritage_3d_assets', 'attribution_text')
    op.drop_column('heritage_3d_assets', 'rights_status')
    op.drop_column('heritage_3d_assets', 'licence_url')
    op.drop_column('heritage_3d_assets', 'licence_name')
    op.drop_column('heritage_3d_assets', 'publisher')
    op.drop_column('heritage_3d_assets', 'creator')
    op.drop_column('heritage_3d_assets', 'source_identifier')
    op.drop_column('heritage_3d_assets', 'source_url')
    op.drop_column('heritage_3d_assets', 'preview_image_key')
    op.drop_column('heritage_3d_assets', 'processed_format')
    op.drop_column('heritage_3d_assets', 'original_format')
    op.drop_column('heritage_3d_assets', 'asset_origin')
