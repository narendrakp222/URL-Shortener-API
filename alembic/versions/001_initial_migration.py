"""Initial migration: Create urls and click_logs tables

Revision ID: 001_initial_migration
Revises: 
Create Date: 2026-09-17 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create urls table
    op.create_table(
        'urls',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('original_url', sa.String(length=2048), nullable=False),
        sa.Column('short_code', sa.String(length=50), nullable=False),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_urls_id'), 'urls', ['id'], unique=False)
    op.create_index(op.f('ix_urls_original_url'), 'urls', ['original_url'], unique=False)
    op.create_index(op.f('ix_urls_short_code'), 'urls', ['short_code'], unique=True)

    # Create click_logs table
    op.create_table(
        'click_logs',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('url_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_click_logs_id'), 'click_logs', ['id'], unique=False)
    op.create_index(op.f('ix_click_logs_url_id'), 'click_logs', ['url_id'], unique=False)
    op.create_index(op.f('ix_click_logs_timestamp'), 'click_logs', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_click_logs_timestamp'), table_name='click_logs')
    op.drop_index(op.f('ix_click_logs_url_id'), table_name='click_logs')
    op.drop_index(op.f('ix_click_logs_id'), table_name='click_logs')
    op.drop_table('click_logs')

    op.drop_index(op.f('ix_urls_short_code'), table_name='urls')
    op.drop_index(op.f('ix_urls_original_url'), table_name='urls')
    op.drop_index(op.f('ix_urls_id'), table_name='urls')
    op.drop_table('urls')
