from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.models.models import Houses
from app.models.models import Properties
from app.models.models import Owner as User
from app.schemas.map_responses import map_house_to_response
from app.schemas.requests import HouseCreateRequest, HouseUpdateRequest
from app.schemas.responses import HouseResponse
from app.storage.gcs import GCStorage


router = APIRouter()

@router.get(
    "/houses",
    response_model=list[HouseResponse],
    description="Get all houses for the current user"
)
async def get_houses(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[HouseResponse]:
    result = await session.execute(
        select(Houses).join(Properties).where(Properties.user_id == current_user.user_id)
    )
    houses = result.scalars().all()

    return [map_house_to_response(house) for house in houses]

@router.get(
    "/houses/{house_id}",
    response_model=HouseResponse,
    description="Get a house by its id"
)
async def get_house(
    house_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> HouseResponse:
    result = await session.execute(
        select(Houses).join(Properties).where(Houses.id == house_id, Properties.user_id == current_user.user_id)
    )
    house = result.scalar_one_or_none()

    if not house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.HOUSE_NOT_FOUND
        )
    
    return map_house_to_response(house)

@router.get(
        "/houses/property/{property_id}",
        response_model=list[HouseResponse],
        description="Get all houses for a property"
)
async def get_houses_by_property(
    property_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[HouseResponse]:
    result = await session.execute(
        select(Houses).join(Properties)
        .where(Houses.propriedade_id == property_id, Properties.user_id == current_user.user_id)
    )
    houses = result.scalars().all()

    if not houses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.HOUSE_NOT_FOUND
        )

    return [map_house_to_response(house) for house in houses]

@router.post(
    "/houses/{property_id}",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new house in a property"
)
async def create_house(
    property_id: int,
    house_data: HouseCreateRequest = Depends(HouseCreateRequest.as_form),
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> HouseResponse:

    query = select(Properties).where(Properties.id == property_id, Properties.user_id == current_user.user_id)
    result = await session.execute(query)
    property = result.scalar_one_or_none()

    if not property:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.USER_WITHOUT_PERMISSION
        )
    
    file_path = None
    if house_data.photo is not None:
        file_path = GCStorage().upload_file(house_data.photo)
    
    new_house = Houses(
        apelido=house_data.nickname,
        foto=file_path,
        qtd_comodos=house_data.room_count,
        banheiros=house_data.bathrooms,
        mobiliada=house_data.furnished,
        status=house_data.status,
        propriedade_id=property_id
    )

    session.add(new_house)
    await session.commit()
    await session.refresh(new_house)

    return map_house_to_response(new_house)

@router.patch(
    "/houses/{house_id}",
    response_model=HouseResponse,
    description="Update a house for the current user"
)
async def update_house(
    house_id: int,
    house_data: HouseUpdateRequest = Depends(HouseUpdateRequest.as_form),
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> HouseResponse:

    result = await session.execute(
        select(Houses)
        .join(Properties)
        .where(Houses.id == house_id, Properties.user_id == current_user.user_id)
    )
    existing_house = result.scalar_one_or_none()
    
    if not existing_house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.HOUSE_NOT_FOUND
        )

    if house_data.photo is not None:
        file_path = GCStorage().upload_file(house_data.photo)
        existing_house.foto = file_path

    existing_house.apelido = house_data.nickname if house_data.nickname is not None else existing_house.apelido
    existing_house.qtd_comodos = house_data.room_count if house_data.room_count is not None else existing_house.qtd_comodos
    existing_house.banheiros = house_data.bathrooms if house_data.bathrooms is not None else existing_house.banheiros
    existing_house.mobiliada = house_data.furnished if house_data.furnished is not None else existing_house.mobiliada
    existing_house.status = house_data.status if house_data.status is not None else existing_house.status

    await session.commit()
    await session.refresh(existing_house)

    return map_house_to_response(existing_house)

@router.delete(
    "/houses/{house_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a house by its id"
)
async def delete_house(
    house_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:

    result = await session.execute(
        select(Houses)
        .join(Properties)
        .where(Houses.id == house_id, Properties.user_id == current_user.user_id)
    )
    existing_house = result.scalar_one_or_none()

    if not existing_house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.HOUSE_NOT_FOUND
        )

    await session.delete(existing_house)
    await session.commit()
