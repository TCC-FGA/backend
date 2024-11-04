from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import List, Optional


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int


class UserResponse(BaseResponse):
    user_id: str
    email: EmailStr
    telephone: str
    hashed_signature: Optional[str]
    cpf: str
    birth_date: date
    name: str
    photo: Optional[str]

    class Config:
        from_attributes = True


class PropertyResponse(BaseModel):
    id: int
    nickname: str
    photo: Optional[str]
    iptu: float
    owner_id: str

    street: Optional[str]
    neighborhood: Optional[str]
    number: Optional[int]
    zip_code: str
    city: Optional[str]
    state: Optional[str]

    class Config:
        from_attributes = True


class HouseResponse(BaseModel):
    id: int
    property_id: int
    photo: Optional[str]
    nickname: str
    room_count: int
    bathrooms: int
    furnished: bool
    status: str

    class Config:
        from_attributes = True


class TenantResponse(BaseModel):
    id: int
    cpf: str
    contact: str
    email: Optional[str]
    name: str
    profession: Optional[str]
    marital_status: Optional[str]
    birth_date: Optional[date]
    emergency_contact: Optional[str]
    income: Optional[float]
    residents: Optional[int]

    street: Optional[str]
    neighborhood: Optional[str]
    number: Optional[int]
    zip_code: str
    city: Optional[str]
    state: Optional[str]

    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    id: int
    template_name: str
    description: Optional[str]
    garage: bool
    warranty: str
    animals: bool
    sublease: bool
    contract_type: str

    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    id: int
    deposit_value: Optional[float]
    start_date: date
    end_date: date
    base_value: float
    due_date: int
    reajustment_rate: Optional[str]
    signed_pdf: Optional[str]
    house_id: int
    template_id: int
    tenant_id: int
    user_id: str
    house: HouseResponse
    tenant: TenantResponse

    class Config:
        from_attributes = True


class ExpenseResponse(BaseModel):
    id: int
    expense_type: str
    value: float
    expense_date: date
    house_id: int

    class Config:
        from_attributes = True


class GuarantorResponse(BaseModel):
    id: int
    tenant_id: int
    cpf: str
    contact: str
    email: Optional[str]
    name: str
    profession: Optional[str]
    marital_status: Optional[str]
    birth_date: Optional[date]
    comment: Optional[str]
    income: Optional[float]

    street: Optional[str]
    neighborhood: Optional[str]
    number: Optional[int]
    zip_code: str
    city: Optional[str]
    state: Optional[str]

    class Config:
        from_attributes = True

class PaymentInstallmentResponse(BaseModel):
    id: int
    installment_value: float
    fg_paid: bool
    payment_type: Optional[str]
    due_date: date
    payment_date: Optional[date]
    contract_id: int

    class Config:
        from_attributes = True
