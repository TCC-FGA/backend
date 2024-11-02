import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Expenses, Houses
import datetime


@pytest.mark.asyncio
async def test_create_expense(
    client: AsyncClient, default_house: Houses, default_user_headers: dict
):
    house_id = default_house.id

    expense_data = {
        "expense_type": "imposto",
        "value": 100,
        "expense_date": "2024-10-30",
    }

    response = await client.post(
        f"/expenses/{house_id}", json=expense_data, headers=default_user_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["expense_type"] == "imposto"
    assert json_response["value"] == 100
    assert json_response["expense_date"] == "2024-10-30"


@pytest.mark.asyncio
async def test_get_expenses(
    client: AsyncClient,
    default_house: Houses,
    session: AsyncSession,
    default_user_headers: dict,
):
    expense = Expenses(
        tipo_despesa="reparo",
        valor=100,
        data_despesa=datetime.date(2024, 10, 30),
        casa_id=default_house.id,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)

    response = await client.get(
        f"/expenses/{default_house.id}", headers=default_user_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["expense_type"] == "reparo"


@pytest.mark.asyncio
async def test_update_expense(
    client: AsyncClient,
    default_house,
    session: AsyncSession,
    default_user_headers: dict,
):
    house_id = default_house.id
    expense = Expenses(
        tipo_despesa="manutenção",
        valor=80,
        data_despesa=datetime.date(2024, 10, 30),
        casa_id=house_id,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)

    update_data = {
        "expense_type": "manutenção",
        "value": 90,
        "expense_date": "2024-10-30",
    }

    response = await client.patch(
        f"/expenses/{expense.id}", json=update_data, headers=default_user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == 90


@pytest.mark.asyncio
async def test_delete_expense(
    client: AsyncClient, default_house:Houses, session: AsyncSession, default_user_headers: dict
):
    house_id = default_house.id
    expense = Expenses(
        tipo_despesa="manutenção",
        valor=150,
        data_despesa=datetime.date(2024, 10, 30),
        casa_id=house_id,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)

    response = await client.delete(f"/expenses/{expense.id}", headers=default_user_headers)
    assert response.status_code == 204

    # Verifica se a despesa foi removida do banco de dados
    deleted_expense = await session.get(Expenses, expense.id)
    assert deleted_expense is None
