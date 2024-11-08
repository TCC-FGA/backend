from datetime import date
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.api import api_messages
from app.main import app
from app.models.models import Owner as User
import pytest

@pytest.mark.asyncio
async def test_register_new_user_status_code(
    client: AsyncClient,
) -> None:
    response = await client.post(
        app.url_path_for("register_new_user"),
        json={
            "email": "test@email.com",
            "password": "testtesttest",
            "photo": "photo",
            "name": "Test User",
            "telephone": "1234567890",
            "hashed_signature": "hashed_signature",
            "cpf": "12345678901",
            "birth_date": "1990-01-01",
            "street": "Test Street",
            "neighborhood": "Test Neighborhood",
            "number": 123,
            "zip_code": "12345678",
            "city": "Test City",
            "state": "DF",            
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.asyncio
async def test_register_new_user_creates_record_in_db(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    await client.post(
        app.url_path_for("register_new_user"),
        json={
            "email": "test@email.com",
            "password": "testtesttest",
            "photo": "photo",
            "name": "Test User",
            "telephone": "1234567890",
            "cpf": "12345678901",
            "birth_date": "1990-01-01",
            "hashed_signature": "hashed_signature",
            "street": "Test Street",
            "neighborhood": "Test Neighborhood",
            "number": 123,
            "zip_code": "12345678",
            "city": "Test City",
            "state": "DF",
        },
    )

    user_count = await session.scalar(
        select(func.count()).where(User.email == "test@email.com")
    )
    assert user_count == 1

@pytest.mark.asyncio
async def test_register_new_user_cannot_create_already_created_user(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    user = User(
        email="test@email.com",
        senha_hash="hashedpassword",
        nome="Test User",
        foto="photo",
        telefone="1234567890",
        cpf="12345678901",
        assinatura_hash="hashed_signature",
        data_nascimento=date(1990, 1, 1),
        rua="Test Street",
        bairro="Test Neighborhood",
        numero=123,
        cep="12345678",
        cidade="Test City",
        estado="DF",
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        app.url_path_for("register_new_user"),
        json={
            "email": "test@email.com",
            "password": "testtesttest",
            "name": "Test User",
            "photo": "photo",
            "telephone": "1234567890",
            "cpf": "12345678901",
            "birth_date": "1990-01-01",
            "hashed_signature": "hashed_signature",
            "street": "Test Street",
            "neighborhood": "Test Neighborhood",
            "number": 123,
            "zip_code": "12345678",
            "city": "Test City",
            "state": "DF",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": api_messages.EMAIL_ADDRESS_ALREADY_USED}