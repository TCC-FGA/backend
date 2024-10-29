"""set default=False in fg_pago(PaymentInstallment)|uniqueTogether in paymentInstallment

Revision ID: 469c9c8f6a62
Revises: 17e782b691a4
Create Date: 2024-10-28 17:13:28.220240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '469c9c8f6a62'
down_revision: Union[str, None] = '17e782b691a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contrato', 'valor_caucao',
               existing_type=sa.NUMERIC(),
               nullable=True)
    op.create_unique_constraint('uq_data_vencimento_contrato_id', 'parcelas', ['data_vencimento', 'contrato_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_data_vencimento_contrato_id', 'parcelas', type_='unique')
    op.alter_column('contrato', 'valor_caucao',
               existing_type=sa.NUMERIC(),
               nullable=False)
    # ### end Alembic commands ###
