from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.api import deps
from app.models.models import Properties
from app.models.models import Owner as User
from app.schemas.map_responses import map_property_to_response
from app.schemas.requests import PropertyCreateRequest, PropertyUpdateRequest
from app.schemas.responses import PropertyResponse


router = APIRouter()


@router.post(
    "/properties",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new property with an address"
)
async def create_property(
    property_data: PropertyCreateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> PropertyResponse:

    new_property = Properties(
        apelido=property_data.nickname,
        foto=property_data.photo,
        iptu=property_data.iptu,
        user_id=current_user.user_id,
        rua=property_data.street,
        bairro=property_data.neighborhood,
        numero=property_data.number,
        cep=property_data.zip_code,
        cidade=property_data.city,
        estado=property_data.state
    )
    session.add(new_property)
    await session.commit()
    await session.refresh(new_property)

    return map_property_to_response(new_property)

@router.patch(
    "/properties/{property_id}",
    response_model=PropertyResponse,
    description="Update a property for the current user"
)
async def update_property(
    property_id: int,
    property_data: PropertyUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> PropertyResponse:

    result = await session.execute(
        select(Properties).where(Properties.id == property_id, Properties.user_id == current_user.user_id)
    )
    existing_property = result.scalar_one_or_none()
    if not existing_property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    existing_property.apelido = property_data.nickname if property_data.nickname is not None else existing_property.apelido
    existing_property.apelido = property_data.nickname if property_data.nickname is not None else existing_property.apelido
    existing_property.foto = property_data.photo if property_data.photo is not None else existing_property.foto
    existing_property.iptu = property_data.iptu if property_data.iptu is not None else existing_property.iptu
    existing_property.rua = property_data.street if property_data.street is not None else existing_property.rua
    existing_property.bairro = property_data.neighborhood if property_data.neighborhood is not None else existing_property.bairro
    existing_property.numero = int(property_data.number) if property_data.number is not None else existing_property.numero
    existing_property.cep = property_data.zip_code if property_data.zip_code is not None else existing_property.cep
    existing_property.cidade = property_data.city if property_data.city is not None else existing_property.cidade
    existing_property.estado = property_data.state if property_data.state is not None else existing_property.estado

    session.add(existing_property)
    await session.commit()
    await session.refresh(existing_property)

    return map_property_to_response(existing_property)


@router.get(
    "/properties",
    response_model=list[PropertyResponse],
    description="Get all properties for the current user"
)
async def get_properties(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[PropertyResponse]:
    result = await session.execute(
        select(Properties).where(Properties.user_id == current_user.user_id)
    )
    properties = result.scalars().all()
    return [map_property_to_response(property) for property in properties]


@router.delete(
    "/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a property for the current user"
)
async def delete_property(
    property_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    result = await session.execute(
        select(Properties).where(Properties.id == property_id, Properties.user_id == current_user.user_id)
    )
    existing_property = result.scalar_one_or_none()
    if not existing_property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    await session.delete(existing_property)
    await session.commit()
