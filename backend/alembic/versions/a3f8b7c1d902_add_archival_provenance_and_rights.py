"""add_archival_provenance_and_rights

Revision ID: a3f8b7c1d902
Revises: f7a3c9b2e5d1
Create Date: 2026-11-07 22:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f8b7c1d902'
down_revision: Union[str, None] = 'f7a3c9b2e5d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Add minimal additive provenance and rights fields to ai_documents
    # ---------------------------------------------------------
    op.add_column(
        'ai_documents',
        sa.Column('source_identifier', sa.String(length=100), nullable=True)
    )
    op.add_column(
        'ai_documents',
        sa.Column('rights_status', sa.String(length=50), server_default='RIGHTS_REVIEW_REQUIRED', nullable=False)
    )
    op.add_column(
        'ai_documents',
        sa.Column('rights_evidence_url', sa.String(length=500), nullable=True)
    )
    op.add_column(
        'ai_documents',
        sa.Column('rights_notes', sa.Text(), nullable=True)
    )
    op.add_column(
        'ai_documents',
        sa.Column('content_origin', sa.String(length=50), server_default='CURATED_SUMMARY', nullable=False)
    )
    op.add_column(
        'ai_documents',
        sa.Column('verification_status', sa.String(length=50), server_default='UNVERIFIED', nullable=False)
    )
    op.add_column(
        'ai_documents',
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_index(op.f('ix_ai_documents_rights_status'), 'ai_documents', ['rights_status'], unique=False)
    op.create_index(op.f('ix_ai_documents_content_origin'), 'ai_documents', ['content_origin'], unique=False)
    op.create_index(op.f('ix_ai_documents_verification_status'), 'ai_documents', ['verification_status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_documents_verification_status'), table_name='ai_documents')
    op.drop_index(op.f('ix_ai_documents_content_origin'), table_name='ai_documents')
    op.drop_index(op.f('ix_ai_documents_rights_status'), table_name='ai_documents')

    op.drop_column('ai_documents', 'verified_at')
    op.drop_column('ai_documents', 'verification_status')
    op.drop_column('ai_documents', 'content_origin')
    op.drop_column('ai_documents', 'rights_notes')
    op.drop_column('ai_documents', 'rights_evidence_url')
    op.drop_column('ai_documents', 'rights_status')
    op.drop_column('ai_documents', 'source_identifier')
