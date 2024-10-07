import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Properties, Owner as User
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_property(session: AsyncSession, client: AsyncClient, default_user_headers: dict)-> None:
    data = {
        "nickname": "Minha Casa",
        "photo": None,
        "iptu": 355.0,
        "street": "Qr 500 Conjunto 1",
        "neighborhood": "Samambaia",
        "number": 30,
        "zip_code": "72301-001",
        "city": "Brasília",
        "state": "DF"
    }

    response = await client.post("/properties", data=data, headers=default_user_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["nickname"] == "Minha Casa"
    assert json_response["iptu"] == 355.0

@pytest.mark.asyncio
async def test_update_property(session: AsyncSession, client: AsyncClient, default_user_headers: dict, default_user: User) -> None:
    new_property = Properties(
        apelido="Casa Antiga",
        iptu=200.0,
        rua="Rua Velha",
        bairro="Bairro Velho",
        numero=10,
        cep="11111-111",
        cidade="Cidade Antiga",
        estado="DF",
        user_id=default_user.user_id 
    )
    session.add(new_property)
    await session.commit()
    await session.refresh(new_property)

    update_data = {
        "nickname": "Casa Atualizada",
        "iptu": 400.0,
        "street": "Rua Nova",
        "neighborhood": "Bairro Novo",
        "number": 20,
        "zip_code": "22222-222",
        "city": "Cidade Nova",
        "state": "DF"
    }

    response = await client.patch(f"/properties/{new_property.id}", data=update_data, headers=default_user_headers)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()

    assert json_response["nickname"] == "Casa Atualizada"
    assert json_response["iptu"] == 400.0
    assert json_response["street"] == "Rua Nova"
    assert json_response["neighborhood"] == "Bairro Novo"
    assert json_response["number"] == 20
    assert json_response["zip_code"] == "22222-222"
    assert json_response["city"] == "Cidade Nova"
    assert json_response["state"] == "DF"

@pytest.mark.asyncio
async def test_get_properties(session: AsyncSession, client: AsyncClient, default_user_headers: dict, default_user: User) -> None:
    property_1 = Properties(
        apelido="Casa 1",
        iptu=100.0,
        rua="Rua 1",
        bairro="Bairro 1",
        numero=1,
        cep="11111-111",
        cidade="Cidade 1",
        estado="DF",
        user_id=default_user.user_id
    )
    property_2 = Properties(
        apelido="Casa 2",
        iptu=200.0,
        rua="Rua 2",
        bairro="Bairro 2",
        numero=2,
        cep="22222-222",
        cidade="Cidade 2",
        estado="DF",
        user_id=default_user.user_id 
    )
    session.add_all([property_1, property_2])
    await session.commit()

    response = await client.get("/properties", headers=default_user_headers)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()

    assert len(json_response) == 2
    assert json_response[0]["nickname"] == "Casa 1"
    assert json_response[1]["nickname"] == "Casa 2"

@pytest.mark.asyncio
async def test_delete_property(session: AsyncSession, client: AsyncClient, default_user_headers: dict, default_user: User) -> None:
    property_to_delete = Properties(
        apelido="Casa Para Deletar",
        iptu=300.0,
        rua="Rua Para Deletar",
        bairro="Bairro Para Deletar",
        numero=30,
        cep="33333-333",
        cidade="Cidade Para Deletar",
        estado="DF",
        user_id=default_user.user_id
    )
    session.add(property_to_delete)
    await session.commit()
    await session.refresh(property_to_delete)

    response = await client.delete(f"/properties/{property_to_delete.id}", headers=default_user_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    result = await session.execute(
        select(Properties).where(Properties.id == property_to_delete.id)
    )
    deleted_property = result.scalar_one_or_none()

    assert deleted_property is None

@pytest.mark.asyncio
async def test_update_nonexistent_property(session: AsyncSession, client: AsyncClient, default_user_headers: dict) -> None:
    update_data = {
        "nickname": "Casa Inexistente",
        "iptu": 500.0
    }

    response = await client.patch("/properties/9999", data=update_data, headers=default_user_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Property not found"

@pytest.mark.asyncio
async def test_delete_nonexistent_property(session: AsyncSession, client: AsyncClient, default_user_headers: dict) -> None:
    response = await client.delete("/properties/9999", headers=default_user_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Property not found"

@pytest.mark.asyncio
async def test_create_property_with_photo(session: AsyncSession, client: AsyncClient, default_user_headers: dict) -> None:
    with open("app/tests/test_files/test_image.jpg", "rb") as image_file:
        # Separar dados e arquivos
        data = {
            "nickname": "Minha Casa com Foto",
            "iptu": 355.0,
            "street": "Qr 500 Conjunto 1",
            "neighborhood": "Samambaia",
            "number": 30,
            "zip_code": "72301-001",
            "city": "Brasília",
            "state": "DF"
        }

        files = {
            "photo": image_file
        }

        response = await client.post("/properties", data=data, files=files, headers=default_user_headers)

        assert response.status_code == status.HTTP_201_CREATED
        json_response = response.json()
        assert json_response["nickname"] == "Minha Casa com Foto"
        assert json_response["iptu"] == 355.0
        assert json_response["photo"] is not None  

@pytest.mark.asyncio
async def test_get_properties_empty(session: AsyncSession, client: AsyncClient, default_user_headers: dict) -> None:
    response = await client.get("/properties", headers=default_user_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

@pytest.mark.asyncio
async def test_partial_update_property(session: AsyncSession, client: AsyncClient, default_user_headers: dict, default_user: User) -> None:
    new_property = Properties(
        apelido="Casa Parcial",
        iptu=200.0,
        rua="Rua Parcial",
        bairro="Bairro Parcial",
        numero=10,
        cep="11111-111",
        cidade="Cidade Parcial",
        estado="DF",
        user_id=default_user.user_id
    )
    session.add(new_property)
    await session.commit()
    await session.refresh(new_property)

    update_data = {
        "nickname": "Casa Parcial Atualizada",
    }

    response = await client.patch(f"/properties/{new_property.id}", data=update_data, headers=default_user_headers)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()

    assert json_response["nickname"] == "Casa Parcial Atualizada"
    assert json_response["iptu"] == 200.0  
    assert json_response["street"] == "Rua Parcial"

@pytest.mark.asyncio
async def test_create_property_invalid_data(session: AsyncSession, client: AsyncClient, default_user_headers: dict) -> None:
    data = {
        "nickname": "Casa Inválida",
        "iptu": "invalido",  # Valor inválido
        "street": "Qr 500 Conjunto 1",
        "neighborhood": "Samambaia",
        "number": 30,
        "zip_code": "72301-001",
        "city": "Brasília",
        "state": "DF"
    }

    response = await client.post("/properties", data=data, headers=default_user_headers)

    # Verifica se a API retorna erro 422
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
