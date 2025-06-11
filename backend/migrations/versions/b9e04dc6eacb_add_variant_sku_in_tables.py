"""add variant_sku in tables

Revision ID: b9e04dc6eacb
Revises: 3b624ea5c568
Create Date: 2025-06-11 18:19:30.962613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9e04dc6eacb'
down_revision = '3b624ea5c568'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Добавляем колонку nullable=True для трёх таблиц
    for table in ('accessories', 'clothing', 'shoes'):
        op.add_column(
            table,
            sa.Column('variant_sku', sa.String(length=100), nullable=True)
        )

    # 2) Бэкап-филл: копируем значения из sku → variant_sku
    op.execute("UPDATE accessories SET variant_sku = sku")
    op.execute("UPDATE clothing SET variant_sku = sku")
    op.execute("UPDATE shoes SET variant_sku = sku")

    # 3) Теперь делаем колонку NOT NULL и перестраиваем индексы
    #    Все операции по индексам и alter_column завернём в batch_alter_table
    with op.batch_alter_table('accessories') as batch_op:
        batch_op.alter_column('variant_sku', nullable=False)
        batch_op.drop_index('ix_accessories_sku')
        batch_op.create_index('ix_accessories_sku', ['sku'], unique=False)
        batch_op.create_index('ix_accessories_brand', ['brand'], unique=False)
        batch_op.create_index('ix_accessories_color', ['color'], unique=False)
        batch_op.create_index('ix_accessories_count_in_stock', ['count_in_stock'], unique=False)
        batch_op.create_index('ix_accessories_price', ['price'], unique=False)
        batch_op.create_index('ix_accessories_subcategory', ['subcategory'], unique=False)
        batch_op.create_index('ix_accessories_variant_sku', ['variant_sku'], unique=True)

    with op.batch_alter_table('clothing') as batch_op:
        batch_op.alter_column('variant_sku', nullable=False)
        batch_op.drop_index('ix_clothing_sku')
        batch_op.create_index('ix_clothing_sku', ['sku'], unique=False)
        batch_op.create_index('ix_clothing_brand', ['brand'], unique=False)
        batch_op.create_index('ix_clothing_color', ['color'], unique=False)
        batch_op.create_index('ix_clothing_count_in_stock', ['count_in_stock'], unique=False)
        batch_op.create_index('ix_clothing_price', ['price'], unique=False)
        batch_op.create_index('ix_clothing_subcategory', ['subcategory'], unique=False)
        batch_op.create_index('ix_clothing_variant_sku', ['variant_sku'], unique=True)

    with op.batch_alter_table('shoes') as batch_op:
        batch_op.alter_column('variant_sku', nullable=False)
        batch_op.drop_index('ix_shoes_sku')
        batch_op.create_index('ix_shoes_sku', ['sku'], unique=False)
        batch_op.create_index('ix_shoes_brand', ['brand'], unique=False)
        batch_op.create_index('ix_shoes_color', ['color'], unique=False)
        batch_op.create_index('ix_shoes_count_in_stock', ['count_in_stock'], unique=False)
        batch_op.create_index('ix_shoes_price', ['price'], unique=False)
        batch_op.create_index('ix_shoes_subcategory', ['subcategory'], unique=False)
        batch_op.create_index('ix_shoes_variant_sku', ['variant_sku'], unique=True)


def downgrade():
    # В downgrade просто удаляем variant_sku и восстанавливаем старые индексы
    with op.batch_alter_table('shoes') as batch_op:
        batch_op.drop_index('ix_shoes_variant_sku')
        batch_op.drop_index('ix_shoes_subcategory')
        batch_op.drop_index('ix_shoes_price')
        batch_op.drop_index('ix_shoes_count_in_stock')
        batch_op.drop_index('ix_shoes_color')
        batch_op.drop_index('ix_shoes_brand')
        batch_op.drop_index('ix_shoes_sku')
        batch_op.create_index('ix_shoes_sku', ['sku'], unique=False)
        batch_op.drop_column('variant_sku')

    with op.batch_alter_table('clothing') as batch_op:
        batch_op.drop_index('ix_clothing_variant_sku')
        batch_op.drop_index('ix_clothing_subcategory')
        batch_op.drop_index('ix_clothing_price')
        batch_op.drop_index('ix_clothing_count_in_stock')
        batch_op.drop_index('ix_clothing_color')
        batch_op.drop_index('ix_clothing_brand')
        batch_op.drop_index('ix_clothing_sku')
        batch_op.create_index('ix_clothing_sku', ['sku'], unique=False)
        batch_op.drop_column('variant_sku')

    with op.batch_alter_table('accessories') as batch_op:
        batch_op.drop_index('ix_accessories_variant_sku')
        batch_op.drop_index('ix_accessories_subcategory')
        batch_op.drop_index('ix_accessories_price')
        batch_op.drop_index('ix_accessories_count_in_stock')
        batch_op.drop_index('ix_accessories_color')
        batch_op.drop_index('ix_accessories_brand')
        batch_op.drop_index('ix_accessories_sku')
        batch_op.create_index('ix_accessories_sku', ['sku'], unique=False)
        batch_op.drop_column('variant_sku')