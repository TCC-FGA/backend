"""generate DB

Revision ID: cd25c31e85eb
Revises: 
Create Date: 2024-09-23 20:39:36.636106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd25c31e85eb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conta_usuario',
    sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('telefone', sa.String(length=20), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('assinatura_hash', sa.String(length=128), nullable=True),
    sa.Column('data_nascimento', sa.Date(), nullable=False),
    sa.Column('cpf', sa.String(length=11), nullable=False),
    sa.Column('senha_hash', sa.String(length=128), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_conta_usuario_email'), 'conta_usuario', ['email'], unique=True)
    op.create_table('inquilino',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cpf', sa.String(length=11), nullable=False),
    sa.Column('contato', sa.String(length=25), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('nome', sa.String(length=255), nullable=False),
    sa.Column('profissao', sa.String(length=255), nullable=True),
    sa.Column('estado_civil', sa.String(length=50), nullable=True),
    sa.Column('data_nascimento', sa.Date(), nullable=True),
    sa.Column('contato_emergencia', sa.String(length=255), nullable=True),
    sa.Column('renda', sa.Numeric(), nullable=True),
    sa.Column('num_residentes', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('rua', sa.String(length=255), nullable=True),
    sa.Column('bairro', sa.String(length=255), nullable=True),
    sa.Column('numero', sa.Integer(), nullable=True),
    sa.Column('cep', sa.String(length=9), nullable=False),
    sa.Column('cidade', sa.String(length=255), nullable=True),
    sa.Column('estado', sa.String(length=2), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inquilino_cpf'), 'inquilino', ['cpf'], unique=True)
    op.create_table('fiador',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cpf', sa.String(length=11), nullable=False),
    sa.Column('contato', sa.String(length=25), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('nome', sa.String(length=255), nullable=False),
    sa.Column('profissao', sa.String(length=255), nullable=True),
    sa.Column('estado_civil', sa.String(length=50), nullable=True),
    sa.Column('data_nascimento', sa.Date(), nullable=True),
    sa.Column('comentario', sa.Text(), nullable=True),
    sa.Column('renda', sa.Numeric(), nullable=True),
    sa.Column('inquilino_id', sa.Integer(), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('rua', sa.String(length=255), nullable=True),
    sa.Column('bairro', sa.String(length=255), nullable=True),
    sa.Column('numero', sa.Integer(), nullable=True),
    sa.Column('cep', sa.String(length=9), nullable=False),
    sa.Column('cidade', sa.String(length=255), nullable=True),
    sa.Column('estado', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['inquilino_id'], ['inquilino.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('inquilino_id')
    )
    op.create_index(op.f('ix_fiador_cpf'), 'fiador', ['cpf'], unique=True)
    op.create_table('propriedades',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('apelido', sa.String(length=100), nullable=False),
    sa.Column('foto', sa.String(length=256), nullable=True),
    sa.Column('iptu', sa.Numeric(), nullable=False),
    sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('rua', sa.String(length=255), nullable=True),
    sa.Column('bairro', sa.String(length=255), nullable=True),
    sa.Column('numero', sa.Integer(), nullable=True),
    sa.Column('cep', sa.String(length=9), nullable=False),
    sa.Column('cidade', sa.String(length=255), nullable=True),
    sa.Column('estado', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['conta_usuario.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('refresh_token',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('refresh_token', sa.String(length=512), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=False),
    sa.Column('exp', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['conta_usuario.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_token_refresh_token'), 'refresh_token', ['refresh_token'], unique=True)
    op.create_table('casas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('apelido', sa.String(length=255), nullable=False),
    sa.Column('qtd_comodos', sa.Integer(), nullable=False),
    sa.Column('banheiros', sa.Integer(), nullable=False),
    sa.Column('mobiliada', sa.Boolean(), nullable=False),
    sa.Column('status', sa.Enum('alugada', 'vaga', 'reforma', name='status'), nullable=False),
    sa.Column('propriedade_id', sa.Integer(), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['propriedade_id'], ['propriedades.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('despesas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tipo_despesa', sa.Enum('manutenção', 'reparo', 'imposto', name='tipo_despesa'), nullable=False),
    sa.Column('valor', sa.Numeric(), nullable=False),
    sa.Column('data_despesa', sa.Date(), nullable=False),
    sa.Column('casa_id', sa.Integer(), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['casa_id'], ['casas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('despesas')
    op.drop_table('casas')
    op.drop_index(op.f('ix_refresh_token_refresh_token'), table_name='refresh_token')
    op.drop_table('refresh_token')
    op.drop_table('propriedades')
    op.drop_index(op.f('ix_fiador_cpf'), table_name='fiador')
    op.drop_table('fiador')
    op.drop_index(op.f('ix_inquilino_cpf'), table_name='inquilino')
    op.drop_table('inquilino')
    op.drop_index(op.f('ix_conta_usuario_email'), table_name='conta_usuario')
    op.drop_table('conta_usuario')
    # ### end Alembic commands ###
