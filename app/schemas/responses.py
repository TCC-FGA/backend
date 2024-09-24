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
    number: Optional[str]
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
