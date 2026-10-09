"""add_artifacts

Revision ID: 41a0966aba1c
Revises: 31a0966aba1b
Create Date: 2026-10-09 11:25:41.367998

"""
from alembic import op
import sqlalchemy as sa

revision = '41a0966aba1c'
down_revision = '31a0966aba1b'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifacts_session_id'), 'artifacts', ['session_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_artifacts_session_id'), table_name='artifacts')
    op.drop_table('artifacts')
