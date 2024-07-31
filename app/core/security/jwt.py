import time

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"


class JWTTokenPayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int


class JWTToken(BaseModel):
    payload: JWTTokenPayload
    access_token: str


def create_jwt_token(user_id: str) -> JWTToken:
    iat = int(time.time())
    exp = iat + get_settings().security.jwt_access_token_expire_secs

    token_payload = JWTTokenPayload(
        iss=get_settings().security.jwt_issuer,
        sub=user_id,
        exp=exp,
        iat=iat,
    )

    access_token = jwt.encode(
        token_payload.model_dump(),
        key=get_settings().security.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )

    return JWTToken(payload=token_payload, access_token=access_token)


def verify_jwt_token(token: str) -> JWTTokenPayload:

    try:
        raw_payload = jwt.decode(
            token,
            get_settings().security.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": True},
            issuer=get_settings().security.jwt_issuer,
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalid: {e}",
        )

    return JWTTokenPayload(**raw_payload)

def generate_reset_token(email: str) -> str:
    iat = int(time.time())
    exp = iat + get_settings().security.jwt_access_token_expire_secs

    token_payload = {
        "iss": get_settings().security.jwt_issuer,
        "sub": email,
        "exp": exp,
        "iat": iat,
        "type": "reset_password"
    }

    reset_token = jwt.encode(
        token_payload,
        key=get_settings().security.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )

    return reset_token

def verify_reset_token(token: str) -> str:
    try:
        raw_payload = jwt.decode(
            token,
            get_settings().security.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": True},
            issuer=get_settings().security.jwt_issuer,
        )

        if raw_payload.get("type") != "reset_password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        return raw_payload["sub"]

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}"
        )