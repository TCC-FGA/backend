import uuid
from datetime import datetime, date

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Uuid, func, Date, Enum, Text, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class Address():
    rua: Mapped[str] = mapped_column(String(255), nullable=True)
    bairro: Mapped[str] = mapped_column(String(255), nullable=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=True)
    cep: Mapped[str] = mapped_column(String(9), nullable=False)
    cidade: Mapped[str] = mapped_column(String(255), nullable=True)
    estado: Mapped[str] = mapped_column(String(2), nullable=True)

class Owner(Base):
    __tablename__ = "conta_usuario"

    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4()))
    foto: Mapped[str] = mapped_column(String(256), nullable=True)
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    assinatura_hash: Mapped[str] = mapped_column(String(128), nullable=True)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")

    propriedades: Mapped[list["Properties"]] = relationship("Properties", back_populates="proprietario", cascade="all, delete-orphan")
    
class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True, index=True)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("conta_usuario.user_id", ondelete="CASCADE"))
    user: Mapped["Owner"] = relationship(back_populates="refresh_tokens")

class Properties(Base, Address):
    __tablename__ = "propriedades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    apelido: Mapped[str] = mapped_column(String(100), nullable=False)
    foto: Mapped[str] = mapped_column(String(256), nullable=True)
    iptu: Mapped[float] = mapped_column(Numeric, nullable=False)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey('conta_usuario.user_id'), nullable=False)
    proprietario: Mapped["Owner"] = relationship("Owner", back_populates="propriedades")
    
    casas: Mapped[list["Houses"]] = relationship("Houses", back_populates="propriedades", cascade="all, delete-orphan")

class Houses(Base):
    __tablename__ = "casas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    apelido: Mapped[str] = mapped_column(String(255), nullable=False)
    foto: Mapped[str] = mapped_column(String(256), nullable=True)
    qtd_comodos: Mapped[int] = mapped_column(Integer, nullable=False)
    banheiros: Mapped[int] = mapped_column(Integer, nullable=False)
    mobiliada: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[enumerate] = mapped_column(Enum("alugada", "vaga", "reforma", name="status"), nullable=False)
    
    propriedade_id: Mapped[int] = mapped_column(ForeignKey('propriedades.id'), nullable=False)
    propriedades: Mapped["Properties"] = relationship("Properties", back_populates="casas")
    despesas: Mapped[list["Expenses"]] = relationship("Expenses", back_populates="casas", cascade="all, delete-orphan")

class Expenses(Base):
    __tablename__ = "despesas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_despesa:Mapped[enumerate] = mapped_column(Enum("manutenção", "reparo", "imposto", name="tipo_despesa"), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric, nullable=False)
    data_despesa: Mapped[date] = mapped_column(Date, nullable=False)

    casa_id: Mapped[int] = mapped_column(ForeignKey('casas.id'), nullable=False)
    casas: Mapped["Houses"] = relationship("Houses", back_populates="despesas")

class Guarantor(Base, Address):
    __tablename__ = "fiador"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True, index=True)
    contato: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    profissao: Mapped[str] = mapped_column(String(255), nullable=True)
    estado_civil: Mapped[str] = mapped_column(String(50), nullable=True)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=True)
    comentario: Mapped[str] = mapped_column(Text, nullable=True)
    renda: Mapped[float] = mapped_column(Numeric, nullable=True)

    inquilino_id: Mapped[int] = mapped_column(ForeignKey('inquilino.id'), nullable=False, unique=True)
    inquilino: Mapped["Tenant"] = relationship("Tenant", back_populates="fiador")

class Tenant(Base, Address):
    __tablename__ = "inquilino"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True, index=True)
    contato: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    profissao: Mapped[str] = mapped_column(String(255), nullable=True)
    estado_civil: Mapped[str] = mapped_column(String(50), nullable=True)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=True)
    contato_emergencia: Mapped[str] = mapped_column(String(255), nullable=True)
    renda: Mapped[float] = mapped_column(Numeric, nullable=True)
    num_residentes: Mapped[int] = mapped_column(Integer, nullable=True)

    fiador: Mapped[int] = relationship("Guarantor", back_populates="inquilino", cascade="all, delete-orphan")
        