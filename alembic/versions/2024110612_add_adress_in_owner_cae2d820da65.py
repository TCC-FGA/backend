"""add adress in owner

Revision ID: cae2d820da65
Revises: 88b55110793b
Create Date: 2024-11-06 17:12:01.551298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cae2d820da65'
down_revision: Union[str, None] = '88b55110793b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conta_usuario', sa.Column('rua', sa.String(length=255), nullable=True))
    op.add_column('conta_usuario', sa.Column('bairro', sa.String(length=255), nullable=True))
    op.add_column('conta_usuario', sa.Column('numero', sa.Integer(), nullable=True))
    op.add_column('conta_usuario', sa.Column('cep', sa.String(length=9), nullable=False))
    op.add_column('conta_usuario', sa.Column('cidade', sa.String(length=255), nullable=True))
    op.add_column('conta_usuario', sa.Column('estado', sa.String(length=2), nullable=True))
    op.add_column('vistoria', sa.Column('pdf_vistoria', sa.String(length=256), nullable=True))
    op.add_column('vistoria', sa.Column('pdf_assinado', sa.String(length=256), nullable=True))
    op.drop_column('vistoria', 'observacao')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vistoria', sa.Column('observacao', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.drop_column('vistoria', 'pdf_vistoria')
    op.drop_column('vistoria', 'pdf_assinado')
    op.drop_column('conta_usuario', 'estado')
    op.drop_column('conta_usuario', 'cidade')
    op.drop_column('conta_usuario', 'cep')
    op.drop_column('conta_usuario', 'numero')
    op.drop_column('conta_usuario', 'bairro')
    op.drop_column('conta_usuario', 'rua')
    # ### end Alembic commands ###
