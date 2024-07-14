"""fix index

Revision ID: 0dbe8ae2836f
Revises: 5db8053fa1d0
Create Date: 2024-07-14 19:57:26.564558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dbe8ae2836f'
down_revision: Union[str, None] = '5db8053fa1d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('patch_voting_index', table_name='best_horoes')
    op.create_index('patch_voting_index', 'best_horoes', ['patch', 'voting'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('patch_voting_index', table_name='best_horoes')
    op.create_index('patch_voting_index', 'best_horoes', ['patch', 'voting'], unique=True)
    # ### end Alembic commands ###
