from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date
from enum import Enum

class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class UserCreateRequest(BaseRequest):
    email: EmailStr
    photo: Optional[str]
    password: str
    name: str
    telephone: str
    hashed_signature: Optional[str] = None
    cpf: str
    birth_date: date

class PropertyCreateRequest(BaseModel):
    nickname: str
    photo: Optional[str]
    iptu: float

    street: Optional[str]
    neighborhood: Optional[str]
    number: Optional[int]
    zip_code: str
    city: Optional[str]
    state: Optional[str]


class PropertyUpdateRequest(BaseModel):
    nickname: Optional[str]
    photo: Optional[str]
    iptu: Optional[float]

    street: Optional[str]
    neighborhood: Optional[str]
    number: Optional[str]
    zip_code: Optional[str]
    city: Optional[str]
    state: Optional[str]

class HouseStatus(str, Enum):
    alugada = "alugada"
    vaga = "vaga"
    reforma = "reforma"

class HouseCreateRequest(BaseModel):
    nickname: str
    rooms: int
    foto: Optional[str]
    bathrooms: int
    furnished: bool = False
    status: HouseStatus
