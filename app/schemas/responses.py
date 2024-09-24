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
    foto: Optional[str]
    telefone: str
    assinatura_hash: Optional[str]
    cpf: str
    data_nascimento: date 
    nome: str

    class Config:
        from_attributes = True


class PropertyResponse(BaseModel):
    id: int
    apelido: str
    foto: Optional[str]
    iptu: float
    user_id: str

    rua: Optional[str]
    bairro: Optional[str]
    numero: Optional[int]
    cep: str
    cidade: Optional[str]
    estado: Optional[str]

    class Config:
        from_attributes = True

class HouseResponse(BaseModel):
    id: int
    propriedade_id: int
    foto: Optional[str]
    apelido: str
    qtd_comodos: int
    banheiros: int
    mobiliada: bool
    status: str
    
    class Config:
        from_attributes = True
