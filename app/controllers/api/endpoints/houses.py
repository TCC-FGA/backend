from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.api import deps
from app.models.models import Houses
from app.models.models import Properties
from app.models.models import Owner as User
from app.schemas.map_responses import map_house_to_response
from app.schemas.requests import HouseCreateRequest
from app.schemas.responses import HouseResponse
from app.storage.gcs import GCStorage


router = APIRouter()


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
            detail="Usuário não tem permissão para acessar esta propriedade"
        )
    
    file_path = None
    if house_data.photo is not None:
        file_path = GCStorage().upload_file(house_data.photo)
    
    new_house = Houses(
        apelido=house_data.nickname,
        foto=file_path,
        qtd_comodos=house_data.rooms,
        banheiros=house_data.bathrooms,
        mobiliada=house_data.furnished,
        status=house_data.status,
        propriedade_id=property_id
    )

    session.add(new_house)
    await session.commit()
    await session.refresh(new_house)

    return map_house_to_response(new_house)

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

