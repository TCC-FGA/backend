from typing import Optional
from fastapi import File, Form, UploadFile
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
    
    nickname: str = Form(...)
    photo: UploadFile | None = File(None)
    iptu: float = Form(...)
    street: Optional[str] = Form(None)
    neighborhood: Optional[str] = Form(None)
    number: Optional[str] = Form(None)
    zip_code: str = Form(...)
    city: Optional[str] = Form(None)
    state: Optional[str] = Form(None)

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(...),
        iptu: float = Form(...),
        photo: UploadFile | None = File(None),
        street: Optional[str] = Form(None),
        neighborhood: Optional[str] = Form(None),
        number: Optional[str] = Form(None),
        zip_code: str = Form(...),
        city: Optional[str] = Form(None),
        state: Optional[str] = Form(None),
    ):
        return cls(
            nickname=nickname,
            iptu=iptu,
            photo=photo,
            street=street,
            neighborhood=neighborhood,
            number=number,
            zip_code=zip_code,
            city=city,
            state=state,
        )


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
    nickname: str = Form(...)
    rooms: int = Form(...)
    photo: UploadFile | None = File(None)
    bathrooms: int = Form(...)
    furnished: bool = Form(False)
    status: HouseStatus = Form(...)

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(...),
        rooms: int = Form(...),
        photo: UploadFile | None = File(None),
        bathrooms: int = Form(...),
        furnished: bool = Form(False),
        status: HouseStatus = Form(...),
    ):
        return cls(
            nickname=nickname,
            rooms=rooms,
            photo=photo,
            bathrooms=bathrooms,
            furnished=furnished,
            status=status,
        )
