"""add user_id in contract and template

Revision ID: 17e782b691a4
Revises: 0e15d3613bd5
Create Date: 2024-10-19 15:52:59.631868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17e782b691a4'
down_revision: Union[str, None] = '0e15d3613bd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contrato', sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=False))
    op.create_foreign_key(None, 'contrato', 'conta_usuario', ['user_id'], ['user_id'])
    op.add_column('template', sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=False))
    op.create_foreign_key(None, 'template', 'conta_usuario', ['user_id'], ['user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'template', type_='foreignkey') # type: ignore
    op.drop_column('template', 'user_id')
    op.drop_constraint(None, 'contrato', type_='foreignkey') # type: ignore
    op.drop_column('contrato', 'user_id')
    # ### end Alembic commands ###
