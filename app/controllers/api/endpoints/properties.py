from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.api import deps
from app.models.models import Properties
from app.models.models import Owner as User
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
        nickname=property_data.nickname,
        photo=property_data.photo,
        iptu=property_data.iptu,
        owner_id=current_user.user_id,
        street=property_data.street,
        neighborhood=property_data.neighborhood,
        number=property_data.number,
        zip_code=property_data.zip_code,
        city=property_data.city,
        state=property_data.state
    )
    session.add(new_property)
    await session.commit()
    await session.refresh(new_property)

    return new_property

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
        select(Properties).where(Properties.id == property_id, Properties.owner_id == current_user.user_id)
    )
    existing_property = result.scalar_one_or_none()
    if not existing_property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    existing_property.nickname = property_data.nickname
    existing_property.photo = property_data.photo
    existing_property.iptu = property_data.iptu
    existing_property.street = property_data.street
    existing_property.neighborhood = property_data.neighborhood
    existing_property.number = property_data.number
    existing_property.zip_code = property_data.zip_code
    existing_property.city = property_data.city
    existing_property.state = property_data.state

    session.add(existing_property)
    await session.commit()
    await session.refresh(existing_property)

    return existing_property


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
        select(Properties).where(Properties.owner_id == current_user.user_id)
    )
    properties = result.scalars().all()
    return properties


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
        select(Properties).where(Properties.id == property_id, Properties.owner_id == current_user.user_id)
    )
    existing_property = result.scalar_one_or_none()
    if not existing_property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    await session.delete(existing_property)
    await session.commit()
