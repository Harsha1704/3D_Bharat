"""create_cultural_knowledge_graph

Revision ID: e6f2b4c81a90
Revises: c4d9a2b71e8f
Create Date: 2026-11-07 15:21:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e6f2b4c81a90'
down_revision: Union[str, None] = 'c4d9a2b71e8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. CREATE TABLE cultural_graph_entities
    # ---------------------------------------------------------
    op.create_table(
        'cultural_graph_entities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('canonical_name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('heritage_site_id', sa.Integer(), nullable=True),
        sa.Column('alternative_names', sa.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('geographical_context', sa.String(length=255), nullable=True),
        sa.Column('period', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), server_default='VERIFIED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['heritage_site_id'], ['heritage_sites.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_cultural_graph_entities_entity_type'), 'cultural_graph_entities', ['entity_type'], unique=False)
    op.create_index(op.f('ix_cultural_graph_entities_canonical_name'), 'cultural_graph_entities', ['canonical_name'], unique=False)
    op.create_index(op.f('ix_cultural_graph_entities_slug'), 'cultural_graph_entities', ['slug'], unique=True)
    op.create_index(op.f('ix_cultural_graph_entities_heritage_site_id'), 'cultural_graph_entities', ['heritage_site_id'], unique=False)
    op.create_index(op.f('ix_cultural_graph_entities_verification_status'), 'cultural_graph_entities', ['verification_status'], unique=False)

    # ---------------------------------------------------------
    # 2. CREATE TABLE cultural_graph_relationships
    # ---------------------------------------------------------
    op.create_table(
        'cultural_graph_relationships',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_entity_id', sa.Integer(), nullable=False),
        sa.Column('target_entity_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('directionality', sa.String(length=20), server_default='DIRECTED', nullable=False),
        sa.Column('evidence_status', sa.String(length=50), server_default='DOCUMENTED', nullable=False),
        sa.Column('confidence_score', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('primary_source_id', sa.Integer(), nullable=True),
        sa.Column('source_citation', sa.Text(), nullable=True),
        sa.Column('historical_period', sa.String(length=255), nullable=True),
        sa.Column('legacy_connection_id', sa.Integer(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('source_entity_id != target_entity_id', name='ck_no_self_relationship'),
        sa.ForeignKeyConstraint(['source_entity_id'], ['cultural_graph_entities.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['target_entity_id'], ['cultural_graph_entities.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['primary_source_id'], ['heritage_sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['legacy_connection_id'], ['heritage_connections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_entity_id', 'target_entity_id', 'relationship_type', name='uq_cultural_relationship')
    )
    op.create_index(op.f('ix_cultural_graph_relationships_source_entity_id'), 'cultural_graph_relationships', ['source_entity_id'], unique=False)
    op.create_index(op.f('ix_cultural_graph_relationships_target_entity_id'), 'cultural_graph_relationships', ['target_entity_id'], unique=False)
    op.create_index(op.f('ix_cultural_graph_relationships_relationship_type'), 'cultural_graph_relationships', ['relationship_type'], unique=False)
    op.create_index(op.f('ix_cultural_graph_relationships_evidence_status'), 'cultural_graph_relationships', ['evidence_status'], unique=False)
    op.create_index(op.f('ix_cultural_graph_relationships_primary_source_id'), 'cultural_graph_relationships', ['primary_source_id'], unique=False)
    op.create_index(op.f('ix_cultural_graph_relationships_legacy_connection_id'), 'cultural_graph_relationships', ['legacy_connection_id'], unique=False)


def downgrade() -> None:
    op.drop_table('cultural_graph_relationships')
    op.drop_table('cultural_graph_entities')
