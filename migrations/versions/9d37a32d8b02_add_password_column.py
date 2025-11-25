"""add password column

Revision ID: 9d37a32d8b02
Revises: e728c03629e3
Create Date: 2025-11-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d37a32d8b02'
down_revision: Union[str, Sequence[str], None] = 'e728c03629e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the column as nullable first
    op.add_column('users', sa.Column('password', sa.String(length=128), nullable=True))
    
    # Set a default password for any existing users so we can make it non-nullable
    op.execute("UPDATE users SET password = 'changeme' WHERE password IS NULL")
    
    # Now make it non-nullable
    op.alter_column('users', 'password', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'password')
