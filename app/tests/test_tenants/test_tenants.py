import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from app.models.models import Tenant, Owner as User

@pytest.mark.asyncio
async def test_create_tenant(client: AsyncClient, default_user_headers: dict) -> None:
    tenant_data = {
        "cpf": "12345678900",
        "contact": "555-5555",
        "email": "tenant@example.com",
        "name": "Test Tenant",
        "profession": "Engineer",
        "marital_status": "Single",
        "birth_date": "1990-01-01",
        "emergency_contact": "555-5556",
        "income": 5000.0,
        "residents": 2,
        "street": "Main St",
        "neighborhood": "Downtown",
        "number": 100,
        "zip_code": "12345-678",
        "city": "Test City",
        "state": "TS"
    }

    response = await client.post(
        "/tenants", json=tenant_data, headers=default_user_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    tenant = response.json()
    assert tenant["cpf"] == "12345678900"
    assert tenant["name"] == "Test Tenant"

@pytest.mark.asyncio
async def test_update_tenant(client: AsyncClient, default_user_headers: dict, default_tenant: Tenant) -> None:
    tenant_id = (await default_tenant).id
    update_data = {
        "name": "Updated Tenant",
        "profession": "Updated Profession"
    }

    response = await client.patch(
        f"/tenants/{tenant_id}", json=update_data, headers=default_user_headers
    )

    assert response.status_code == status.HTTP_200_OK
    updated_tenant = response.json()
    assert updated_tenant["name"] == "Updated Tenant"
    assert updated_tenant["profession"] == "Updated Profession"

@pytest.mark.asyncio
async def test_get_tenant(client: AsyncClient, default_user_headers: dict, default_tenant: Tenant) -> None:
    tenant_id = (await default_tenant).id

    response = await client.get(
        f"/tenants/{tenant_id}", headers=default_user_headers
    )

    assert response.status_code == status.HTTP_200_OK
    tenant = response.json()
    assert tenant["id"] == tenant_id

@pytest.mark.asyncio
async def test_delete_tenant(client: AsyncClient, default_user_headers: dict, default_tenant: Tenant) -> None:
    tenant_id = (await default_tenant).id

    response = await client.delete(
        f"/tenants/{tenant_id}", headers=default_user_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
