from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.models.models import Guarantor, Tenant
from app.models.models import Owner as User
from app.schemas.map_responses import map_guarantor_to_response
from app.schemas.requests import GuarantorCreateRequest, GuarantorUpdateRequest
from app.schemas.responses import GuarantorResponse


router = APIRouter()


@router.get(
    "/guarantor/{tenant_id}",
    response_model=GuarantorResponse,
    description="Get the guarantor by id of the tenant",
)
async def get_guarantor_by_tenant_id(
    tenant_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> GuarantorResponse:
    result = await session.execute(
        select(Guarantor).where(Guarantor.inquilino_id == tenant_id)
    )
    guarantor = result.scalar_one_or_none()

    if not guarantor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.GUARANTOR_NOT_FOUND,
        )

    return map_guarantor_to_response(guarantor)


@router.post(
    "/guarantor/{tenant_id}",
    response_model=GuarantorResponse,
    description="Create a new guarantor for the tenant",
    status_code=status.HTTP_201_CREATED,
)
async def create_guarantor(
    guarantor_data: GuarantorCreateRequest,
    tenant_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> GuarantorResponse:

    new_guarantor = Guarantor(
        inquilino_id=tenant_id,
        cpf=guarantor_data.cpf,
        contato=guarantor_data.contact,
        email=guarantor_data.email,
        nome=guarantor_data.name,
        profissao=guarantor_data.profession,
        estado_civil=guarantor_data.marital_status,
        data_nascimento=guarantor_data.birth_date,
        comentario=guarantor_data.comment,
        renda=guarantor_data.income,
        rua=guarantor_data.street,
        bairro=guarantor_data.neighborhood,
        numero=guarantor_data.number,
        cep=guarantor_data.zip_code,
        cidade=guarantor_data.city,
        estado=guarantor_data.state,
    )

    session.add(new_guarantor)
    await session.commit()
    await session.refresh(new_guarantor)

    return map_guarantor_to_response(new_guarantor)


@router.patch(
    "/guarantor/{guarantor_id}",
    response_model=GuarantorResponse,
    description="Update a guarantor",
    status_code=status.HTTP_200_OK,
)
async def update_guarantor(
    guarantor_id: int,
    guarantor_data: GuarantorUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> GuarantorResponse:
    result = await session.execute(
        select(Guarantor).filter(Guarantor.id == guarantor_id)
    )
    existing_guarantor = result.scalar_one_or_none()

    if not existing_guarantor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.GUARANTOR_NOT_FOUND,
        )

    existing_guarantor.contato = (
        guarantor_data.contact
        if guarantor_data.contact is not None
        else existing_guarantor.contato
    )
    existing_guarantor.email = (
        guarantor_data.email
        if guarantor_data.email is not None
        else existing_guarantor.email
    )
    existing_guarantor.nome = (
        guarantor_data.name
        if guarantor_data.name is not None
        else existing_guarantor.nome
    )
    existing_guarantor.profissao = (
        guarantor_data.profession
        if guarantor_data.profession is not None
        else existing_guarantor.profissao
    )
    existing_guarantor.estado_civil = (
        guarantor_data.marital_status
        if guarantor_data.marital_status is not None
        else existing_guarantor.estado_civil
    )
    existing_guarantor.data_nascimento = (
        guarantor_data.birth_date
        if guarantor_data.birth_date is not None
        else existing_guarantor.data_nascimento
    )
    existing_guarantor.comentario = (
        guarantor_data.comment
        if guarantor_data.comment is not None
        else existing_guarantor.comentario
    )
    existing_guarantor.renda = (
        guarantor_data.income
        if guarantor_data.income is not None
        else existing_guarantor.renda
    )
    existing_guarantor.rua = (
        guarantor_data.street
        if guarantor_data.street is not None
        else existing_guarantor.rua
    )
    existing_guarantor.bairro = (
        guarantor_data.neighborhood
        if guarantor_data.neighborhood is not None
        else existing_guarantor.bairro
    )
    existing_guarantor.numero = (
        guarantor_data.number
        if guarantor_data.number is not None
        else existing_guarantor.numero
    )
    existing_guarantor.cep = (
        guarantor_data.zip_code
        if guarantor_data.zip_code is not None
        else existing_guarantor.cep
    )
    existing_guarantor.cidade = (
        guarantor_data.city
        if guarantor_data.city is not None
        else existing_guarantor.cidade
    )
    existing_guarantor.estado = (
        guarantor_data.state
        if guarantor_data.state is not None
        else existing_guarantor.estado
    )

    await session.commit()
    await session.refresh(existing_guarantor)

    return map_guarantor_to_response(existing_guarantor)


@router.delete(
    "/guarantor/{guarantor_id}",
    description="Delete a guarantor",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_guarantor(
    guarantor_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    result = await session.execute(
        select(Guarantor)
        .options(selectinload(Guarantor.inquilino))
        .where(Guarantor.id == guarantor_id)
    )
    guarantor = result.scalar_one_or_none()

    if not guarantor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.GUARANTOR_NOT_FOUND,
        )

    if guarantor.inquilino.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.FORBIDDEN_GUARANTOR,
        )

    await session.delete(guarantor)
    await session.commit()

