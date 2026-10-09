"""add_chat_tables

Revision ID: 31a0966aba1b
Revises: 21a0966aba1a
Create Date: 2026-10-09 11:20:41.367998

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = '31a0966aba1b'
down_revision = '21a0966aba1a'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_session_id'), 'messages', ['session_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_messages_session_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_table('sessions')
