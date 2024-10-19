import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Template, Owner as User


@pytest.mark.asyncio
async def test_create_template(client: AsyncClient, session: AsyncSession, default_user_headers: dict) -> None:
    template_data = {
        "template_name": "Template Teste",
        "description": "Descrição do template",
        "garage": True,
        "warranty": "caução",
        "animals": True,
        "sublease": False,
        "contract_type": "residencial"
    }

    response = await client.post(
        "/templates",
        json=template_data,
        headers=default_user_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["template_name"] == "Template Teste"
    assert json_response["description"] == "Descrição do template"
    assert json_response["garage"] == True
    assert json_response["warranty"] == "caução"
    assert json_response["animals"] == True
    assert json_response["sublease"] == False
    assert json_response["contract_type"] == "residencial"


@pytest.mark.asyncio
async def test_get_templates(client: AsyncClient, session: AsyncSession, default_user_headers: dict) -> None:
    template_data = {
        "template_name": "Template Teste",
        "description": "Descrição do template",
        "garage": True,
        "warranty": "caução",
        "animals": True,
        "sublease": False,
        "contract_type": "residencial"
    }

    await client.post(
        "/templates",
        json=template_data,
        headers=default_user_headers
    )

    response = await client.get("/templates", headers=default_user_headers)
    
    assert response.status_code == status.HTTP_200_OK
    templates = response.json()
    assert len(templates) > 0
    assert templates[0]["template_name"] == "Template Teste"


@pytest.mark.asyncio
async def test_update_template(
    client: AsyncClient, 
    session: AsyncSession, 
    default_user_headers: dict, 
    default_template: Template
) -> None:
    template = default_template

    update_data = {
        "template_name": "Template Atualizado",
        "description": "Nova descrição",
        "garage": False,
        "warranty": "fiador"
    }

    response = await client.patch(
        f"/templates/{template.id}",
        headers=default_user_headers,
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["template_name"] == update_data["template_name"]
    assert json_response["description"] == update_data["description"]
    assert json_response["garage"] == update_data["garage"]
    assert json_response["warranty"] == update_data["warranty"]


@pytest.mark.asyncio
async def test_delete_template(
    client: AsyncClient, 
    session: AsyncSession, 
    default_user_headers: dict, 
    default_template: Template
) -> None:
    template = default_template

    response = await client.delete(
        f"/templates/{template.id}",
        headers=default_user_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
