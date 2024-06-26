"""Update table results

Revision ID: 4aedbe307aa8
Revises: 963180871d8e
Create Date: 2024-05-13 17:04:19.461059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4aedbe307aa8'
down_revision: Union[str, None] = '963180871d8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quiz_results', sa.Column('total_correct_answers', sa.Integer(), nullable=False))
    op.add_column('quiz_results', sa.Column('total_questions_answered', sa.Integer(), nullable=False))
    op.alter_column('quiz_results', 'score',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('quiz_results', 'score',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.drop_column('quiz_results', 'total_questions_answered')
    op.drop_column('quiz_results', 'total_correct_answers')
    # ### end Alembic commands ###
