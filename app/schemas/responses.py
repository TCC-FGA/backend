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

    class Config:
        from_attributes = True