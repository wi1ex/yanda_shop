"""change size_label type in Shoe

Revision ID: 858e670d417c
Revises: 0598f3d11ecb
Create Date: 2025-07-04 12:01:00.976262
"""
from alembic import op
import sqlalchemy as sa

revision = '858e670d417c'
down_revision = '0598f3d11ecb'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('shoes', schema=None) as batch_op:
        batch_op.alter_column(
            'size_label',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            type_=sa.String(length=100),
            existing_nullable=True,
            postgresql_using="size_label::text"
        )

def downgrade():
    with op.batch_alter_table('shoes', schema=None) as batch_op:
        batch_op.alter_column(
            'size_label',
            existing_type=sa.String(length=100),
            type_=sa.DOUBLE_PRECISION(precision=53),
            existing_nullable=True,
            postgresql_using="size_label::numeric"
        )
