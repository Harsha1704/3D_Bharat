"""create_ai_rag_tables

Revision ID: f7a3c9b2e5d1
Revises: e6f2b4c81a90
Create Date: 2026-11-07 15:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7a3c9b2e5d1'
down_revision: Union[str, None] = 'e6f2b4c81a90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. CREATE TABLE ai_documents
    # ---------------------------------------------------------
    op.create_table(
        'ai_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('publisher_institution', sa.String(length=255), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('publication_date', sa.String(length=100), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('permission_classification', sa.String(length=50), server_default='PUBLIC_HERITAGE_ARCHIVE', nullable=False),
        sa.Column('total_chunks', sa.Integer(), server_default='0', nullable=False),
        sa.Column('heritage_site_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['heritage_site_id'], ['heritage_sites.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )
    op.create_index(op.f('ix_ai_documents_document_id'), 'ai_documents', ['document_id'], unique=True)
    op.create_index(op.f('ix_ai_documents_title'), 'ai_documents', ['title'], unique=False)
    op.create_index(op.f('ix_ai_documents_document_type'), 'ai_documents', ['document_type'], unique=False)
    op.create_index(op.f('ix_ai_documents_content_hash'), 'ai_documents', ['content_hash'], unique=False)
    op.create_index(op.f('ix_ai_documents_heritage_site_id'), 'ai_documents', ['heritage_site_id'], unique=False)

    # ---------------------------------------------------------
    # 2. CREATE TABLE ai_document_chunks
    # ---------------------------------------------------------
    op.create_table(
        'ai_document_chunks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('chunk_hash', sa.String(length=64), nullable=False),
        sa.Column('token_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('section_heading', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['ai_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'chunk_index', name='uq_doc_chunk_index')
    )
    op.create_index(op.f('ix_ai_document_chunks_document_id'), 'ai_document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_ai_document_chunks_chunk_hash'), 'ai_document_chunks', ['chunk_hash'], unique=False)

    # ---------------------------------------------------------
    # 3. CREATE TABLE ai_chunk_embeddings
    # ---------------------------------------------------------
    op.create_table(
        'ai_chunk_embeddings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chunk_id', sa.Integer(), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('dimensions', sa.Integer(), nullable=False),
        sa.Column('embedding_json', sa.JSON(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chunk_id'], ['ai_document_chunks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chunk_id', 'embedding_model', name='uq_chunk_embedding_model')
    )
    op.create_index(op.f('ix_ai_chunk_embeddings_chunk_id'), 'ai_chunk_embeddings', ['chunk_id'], unique=False)
    op.create_index(op.f('ix_ai_chunk_embeddings_embedding_model'), 'ai_chunk_embeddings', ['embedding_model'], unique=False)
    op.create_index(op.f('ix_ai_chunk_embeddings_content_hash'), 'ai_chunk_embeddings', ['content_hash'], unique=False)


def downgrade() -> None:
    op.drop_table('ai_chunk_embeddings')
    op.drop_table('ai_document_chunks')
    op.drop_table('ai_documents')
