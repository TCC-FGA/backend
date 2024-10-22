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

class UserUpdateRequest(BaseModel):
    telephone: Optional[str] = None
    name: Optional[str] = None
    hashed_signature: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class UserCreateRequest(BaseRequest):
    email: EmailStr
    photo: Optional[str] = None
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
    number: Optional[int] = Form(None)
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
            number=int(number) if number is not None else None,
            zip_code=zip_code,
            city=city,
            state=state,
        )

class PropertyUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    photo: UploadFile | None = File(None)
    iptu: Optional[float] = None 

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(None),
        photo: UploadFile | None = File(None),
        iptu: float = Form(None),
        street: str = Form(None),
        neighborhood: str = Form(None),
        number: str = Form(None),
        zip_code: str = Form(None),
        city: str = Form(None),
        state: str = Form(None),
    ):
        return cls(
            nickname=nickname,
            photo=photo,
            iptu=iptu,
            street=street,
            neighborhood=neighborhood,
            number=int(number) if number is not None else None,
            zip_code=zip_code,
            city=city,
            state=state,
        )

class HouseStatus(str, Enum):
    alugada = "alugada"
    vaga = "vaga"
    reforma = "reforma"

class HouseCreateRequest(BaseModel):
    nickname: str = Form(...)
    room_count: int = Form(...)
    photo: UploadFile | None = File(None)
    bathrooms: int = Form(...)
    furnished: bool = Form(False)
    status: HouseStatus = Form(...)

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(...),
        room_count: int = Form(...),
        photo: UploadFile | None = File(None),
        bathrooms: int = Form(...),
        furnished: bool = Form(False),
        status: HouseStatus = Form(...),
    ):
        return cls(
            nickname=nickname,
            room_count=room_count,
            photo=photo,
            bathrooms=bathrooms,
            furnished=furnished,
            status=status,
        )

class HouseUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    photo: UploadFile | None = File(None)
    room_count: Optional[int] = None
    bathrooms: Optional[int] = None 
    furnished: Optional[bool] = None
    status: Optional[HouseStatus]

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(None),
        room_count: int = Form(None),
        photo: UploadFile | None = File(None),
        bathrooms: int = Form(None),
        furnished: bool = Form(False),
        status: HouseStatus = Form(None),
    ):
        return cls(
            nickname=nickname,
            room_count=room_count,
            photo=photo,
            bathrooms=bathrooms,
            furnished=furnished,
            status=status,
        )

class TenantCreateRequest(BaseModel):
    cpf: str
    contact: str
    email: Optional[str] = None
    name: str
    profession: Optional[str] = None
    marital_status: Optional[str] = None
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    income: Optional[float] = None
    residents: Optional[int] = None

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: str
    city: Optional[str] = None
    state: Optional[str] = None

class TenantUpdateRequest(BaseModel):
    cpf: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    profession: Optional[str] = None
    marital_status: Optional[str] = None
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    income: Optional[float] = None
    residents: Optional[int] = None

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class ContractType(str, Enum):
    residencial = "residencial"
    comercial = "comercial"

class Warranty(str, Enum):
    fiador = "fiador"
    caução = "caução"
    nenhum = "nenhum"

class TemplateCreateRequest(BaseModel):
    template_name: str
    description: Optional[str] = None
    garage: bool
    warranty: Warranty
    animals: bool
    sublease: bool
    contract_type: ContractType

class TemplateUpdateRequest(BaseModel):
    template_name: Optional[str] = None
    description: Optional[str] = None
    garage: Optional[bool] = None
    warranty: Optional[Warranty] = None
    animals: Optional[bool] = None
    sublease: Optional[bool] = None
    contract_type: Optional[ContractType] = None

class ReajustmentRate(str, Enum):
    igpm = "igpm"

class ContractCreateRequest(BaseModel):
    deposit_value: Optional[float] = None
    start_date: date
    end_date: date
    base_value: float
    due_date: int
    reajustment_rate: Optional[ReajustmentRate] = None
    house_id: int
    template_id: int
    tenant_id: int
