import uuid
from datetime import datetime, date

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Uuid, func, Float, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Owner(Base):
    __tablename__ = "user_account"

    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    telephone: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_signature: Mapped[str] = mapped_column(String(128), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    
class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True, index=True)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.user_id", ondelete="CASCADE"))
    user: Mapped["Owner"] = relationship(back_populates="refresh_tokens")