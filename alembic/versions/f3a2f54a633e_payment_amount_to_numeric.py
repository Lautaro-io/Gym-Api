"""payment amount to numeric

Revision ID: f3a2f54a633e
Revises: 71888d10d80f
Create Date: 2026-10-23 21:18:46.088907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f3a2f54a633e'
down_revision: Union[str, Sequence[str], None] = '71888d10d80f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cambia payment.amount de FLOAT a NUMERIC(10, 2)."""
    op.alter_column('payment', 'amount',
               existing_type=sa.FLOAT(precision=53),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)


def downgrade() -> None:
    """Revierte payment.amount a FLOAT."""
    op.alter_column('payment', 'amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.FLOAT(precision=53),
               existing_nullable=False)
