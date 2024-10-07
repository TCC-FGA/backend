import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Houses, Properties, Owner as User

@pytest.mark.asyncio
async def test_create_house(client: AsyncClient, session: AsyncSession, default_user_headers: dict, default_property: Properties) -> None:
    property_id = default_property.id

    house_data = {
        "nickname": "Casa Teste",
        "room_count": 3,
        "bathrooms": 2,
        "furnished": False,
        "status": "vaga",
    }

    response = await client.post(
        f"/houses/{property_id}",
        data=house_data,
        headers=default_user_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["nickname"] == "Casa Teste"
    assert json_response["room_count"] == 3
    assert json_response["bathrooms"] == 2
    assert json_response["furnished"] == False
    assert json_response["status"] == "vaga"

@pytest.mark.asyncio
async def test_get_houses(client: AsyncClient, session: AsyncSession, default_user_headers: dict, default_property: Properties) -> None:
    property_id = default_property.id 

    house_data = {
        "nickname": "Casa Teste",
        "room_count": 3,
        "bathrooms": 2,
        "furnished": False,
        "status": "vaga",
    }
    await client.post(
        f"/houses/{property_id}",
        data=house_data,
        headers=default_user_headers
    )

    response = await client.get(f"/houses", headers=default_user_headers)
    
    assert response.status_code == status.HTTP_200_OK
    houses = response.json()
    assert len(houses) > 0  

@pytest.mark.asyncio
async def test_update_house(
    client: AsyncClient, 
    session: AsyncSession, 
    default_user_headers: dict, 
    default_house: Houses
) -> None:
    house = default_house

    update_data = {
        "nickname": "Casa Atualizada",
        "room_count": "4",
        "bathrooms": "3"
    }

    response = await client.patch(
        f"/houses/{house.id}",
        headers=default_user_headers,
        data=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["nickname"] == update_data["nickname"]
    assert json_response["room_count"] == int(update_data["room_count"])

@pytest.mark.asyncio
async def test_delete_house(
    client: AsyncClient, 
    session: AsyncSession, 
    default_user_headers: dict, 
    default_house: Houses
) -> None:
    house = default_house

    response = await client.delete(
        f"/houses/{house.id}",
        headers=default_user_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
