"""Add cascade delete

Revision ID: 587b4bd5f4a0
Revises: d4516204ea71
Create Date: 2024-04-29 16:58:26.974675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '587b4bd5f4a0'
down_revision: Union[str, None] = 'd4516204ea71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###