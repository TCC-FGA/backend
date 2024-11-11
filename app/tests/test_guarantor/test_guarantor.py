import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Guarantor, Tenant
import datetime


@pytest.mark.asyncio
async def test_create_guarantor(
    client: AsyncClient, default_tenant: Tenant, default_user_headers: dict
):
    tenant_id = default_tenant.id

    guarantor_data = {
        "cpf": "98765432100",
        "contact": "555-5556",
        "email": "guarantor@mail.com",
        "name": "Jane Doe",
        "profession": "Teacher",
        "marital_status": "casado",
        "birth_date": "1985-05-15",
        "comment": "Good financial stability",
        "income": 7000.0,
        "street": "Rua Guarantor",
        "neighborhood": "Bairro Guarantor",
        "number": 101,
        "zip_code": "12345-678",
        "city": "Cidade Guarantor",
        "state": "SP",
    }

    response = await client.post(
        f"/guarantor/{tenant_id}", json=guarantor_data, headers=default_user_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["cpf"] == "98765432100"
    assert json_response["name"] == "Jane Doe"
    assert json_response["income"] == 7000.0


@pytest.mark.asyncio
async def test_get_guarantor_by_tenant_id(
    client: AsyncClient,
    default_tenant: Tenant,
    session: AsyncSession,
    default_user_headers: dict,
):
    guarantor = Guarantor(
        cpf="12345678900",
        contato="555-5555",
        email="testeguardian@mail.com",
        nome="Guardian Test",
        profissao="Accountant",
        estado_civil="solteiro",
        data_nascimento=datetime.date(1990, 1, 1),
        renda=6000.0,
        inquilino_id=default_tenant.id,
        rua="Rua Teste",
        bairro="Bairro Teste",
        numero=1,
        cep="11111-111",
        cidade="Cidade Teste",
        estado="DF",
    )

    session.add(guarantor)
    await session.commit()
    await session.refresh(guarantor)

    response = await client.get(
        f"/guarantor/{default_tenant.id}", headers=default_user_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cpf"] == "12345678900"
    assert data["name"] == "Guardian Test"


@pytest.mark.asyncio
async def test_update_guarantor(
    client: AsyncClient,
    default_tenant: Tenant,
    session: AsyncSession,
    default_user_headers: dict,
):
    guarantor = Guarantor(
        cpf="8765432100",
        contato="555-5556",
        email="oldemail@mail.com",
        nome="Old Name",
        profissao="Engineer",
        estado_civil="solteiro",
        data_nascimento=datetime.date(1985, 5, 15),
        renda=8000.0,
        inquilino_id=default_tenant.id,
        rua="Rua Teste",
        bairro="Bairro Teste",
        numero=1,
        cep="11111-111",
        cidade="Cidade Teste",
        estado="DF",
    )
    session.add(guarantor)
    await session.commit()
    await session.refresh(guarantor)

    update_data = {
        "name": "Updated Name",
        "income": 9000.0,
        "email": "newemail@mail.com",
    }

    response = await client.patch(
        f"/guarantor/{guarantor.id}", json=update_data, headers=default_user_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["income"] == 9000.0
    assert data["email"] == "newemail@mail.com"


@pytest.mark.asyncio
async def test_delete_guarantor(
    client: AsyncClient,
    default_tenant: Tenant,
    session: AsyncSession,
    default_user_headers: dict,
):
    guarantor = Guarantor(
        cpf="8765432100",
        contato="555-5557",
        email="deleteguard@mail.com",
        nome="Delete Guard",
        profissao="Lawyer",
        estado_civil="casado",
        data_nascimento=datetime.date(1980, 10, 20),
        renda=7500.0,
        inquilino_id=default_tenant.id,
        rua="Rua Teste",
        bairro="Bairro Teste",
        numero=1,
        cep="11111-111",
        cidade="Cidade Teste",
        estado="DF",
    )
    session.add(guarantor)
    await session.commit()
    await session.refresh(guarantor)

    response = await client.delete(
        f"/guarantor/{guarantor.id}", headers=default_user_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted_guarantor = await session.get(Guarantor, guarantor.id)
    assert deleted_guarantor is None
