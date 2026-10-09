"""initial_schema

Revision ID: 21a0966aba1a
Revises: 
Create Date: 2026-10-09 11:14:41.367998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21a0966aba1a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import pgvector.sqlalchemy

def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('guest_slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=False),
        sa.Column('metadata_json', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_guest_slug'), 'documents', ['guest_slug'], unique=False)
    
    op.create_table(
        'chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('speaker', sa.String(), nullable=True),
        sa.Column('timestamp', sa.String(), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(768), nullable=True),
        sa.Column('search_vector', sa.dialects.postgresql.TSVECTOR(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute('CREATE INDEX ix_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops);')
    op.execute("CREATE INDEX ix_chunks_search_vector ON chunks USING gin (search_vector);")
    op.execute("""
    CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
    ON chunks FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(search_vector, 'pg_catalog.english', text);
    """)

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS tsvectorupdate ON chunks;")
    op.drop_index('ix_chunks_search_vector', table_name='chunks')
    op.drop_index('ix_chunks_embedding', table_name='chunks')
    op.drop_table('chunks')
    op.drop_index(op.f('ix_documents_guest_slug'), table_name='documents')
    op.drop_table('documents')
