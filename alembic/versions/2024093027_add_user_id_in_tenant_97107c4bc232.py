"""add user_id in tenant

Revision ID: 97107c4bc232
Revises: 9c0f053591fc
Create Date: 2024-09-30 15:27:46.209280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97107c4bc232'
down_revision: Union[str, None] = '9c0f053591fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inquilino', sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=False))
    op.create_foreign_key(None, 'inquilino', 'conta_usuario', ['user_id'], ['user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'inquilino', type_='foreignkey') # type: ignore
    op.drop_column('inquilino', 'user_id')
    # ### end Alembic commands ###