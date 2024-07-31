"""new_db

Revision ID: 6e71853ddc20
Revises: 1649d3e112c5
Create Date: 2024-07-30 20:11:23.911560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e71853ddc20'
down_revision: Union[str, None] = '1649d3e112c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_account', sa.Column('hashed_signature', sa.String(length=128), nullable=False))
    op.drop_column('user_account', 'monthly_income')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_account', sa.Column('monthly_income', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.drop_column('user_account', 'hashed_signature')
    # ### end Alembic commands ###
