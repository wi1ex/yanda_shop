"""delete username, password_hash and author_name columns

Revision ID: 75bfe4da00dd
Revises: 610383dbf3c4
Create Date: 2025-08-05 03:16:22.942032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75bfe4da00dd'
down_revision = '610383dbf3c4'
branch_labels = None
depends_on = None


def upgrade():
    # Удаляем из users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_hash')
        batch_op.drop_column('username')

    # Удаляем из change_logs
    with op.batch_alter_table('change_logs', schema=None) as batch_op:
        batch_op.drop_column('author_name')


def downgrade():
    # Восстанавливаем в users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.VARCHAR(length=50), nullable=False))
        batch_op.add_column(sa.Column('password_hash', sa.VARCHAR(), nullable=True))

    # Восстанавливаем в change_logs
    with op.batch_alter_table('change_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_name', sa.VARCHAR(length=50), nullable=False))
