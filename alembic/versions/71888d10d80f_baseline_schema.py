"""baseline schema

Revision ID: 71888d10d80f
Revises:
Create Date: 2026-10-23 21:18:08.338495

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '71888d10d80f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline: la base ya existia con este esquema."""
    pass


def downgrade() -> None:
    pass
