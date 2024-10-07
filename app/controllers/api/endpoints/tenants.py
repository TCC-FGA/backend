from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.models.models import Tenant
from app.models.models import Owner as User
from app.schemas.map_responses import map_tenant_to_response
from app.schemas.map_responses import TenantResponse
from app.schemas.requests import TenantCreateRequest, TenantUpdateRequest

import logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/tenants",
    response_model=list[TenantResponse],
    description="Get all tenants for the current user",
    status_code=status.HTTP_200_OK
)
async def get_tenants(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[TenantResponse]:
    result = await session.execute(
        select(Tenant).join(User).where(User.user_id == current_user.user_id)
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TENANT_NOT_FOUND
        )

    tenants = result.scalars().all()

    return [map_tenant_to_response(tenant) for tenant in tenants]

@router.get(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,
    description="Get a tenant by its id",
    status_code=status.HTTP_200_OK
)
async def get_tenant(
    tenant_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> TenantResponse:
    result = await session.execute(
        select(Tenant).join(User).where(Tenant.id == tenant_id, User.user_id == current_user.user_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TENANT_NOT_FOUND
        )

    return map_tenant_to_response(tenant)

@router.post(
    "/tenants",
    response_model=TenantResponse,
    description="Create a new tenant",
    status_code=status.HTTP_201_CREATED
)
async def create_tenant(
    tenant_request: TenantCreateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> TenantResponse:
    
    existing_tenant = await session.execute(
        select(Tenant).where(Tenant.cpf == tenant_request.cpf, Tenant.user_id == current_user.user_id)
    )
    logger.debug(f"Existing tenant: {existing_tenant}")
    tenant = existing_tenant.scalar_one_or_none()

    if tenant:
        logger.info("Tenant already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.TENANT_ALREADY_EXISTS
        )
    
    tenant = Tenant(
        cpf=tenant_request.cpf,
        contato=tenant_request.contact,
        email=tenant_request.email,
        nome=tenant_request.name,
        profissao=tenant_request.profession,
        estado_civil=tenant_request.marital_status,
        data_nascimento=tenant_request.birth_date,
        contato_emergencia=tenant_request.emergency_contact,
        renda=tenant_request.income,
        num_residentes=tenant_request.residents,
        rua=tenant_request.street,
        bairro=tenant_request.neighborhood,
        numero=tenant_request.number,
        cep=tenant_request.zip_code,
        cidade=tenant_request.city,
        estado=tenant_request.state,
        user_id=current_user.user_id
    )

    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)

    return map_tenant_to_response(tenant)

@router.patch(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,
    description="Update a tenant",
    status_code=status.HTTP_200_OK
)
async def update_tenant(
    tenant_id: int,
    tenant_request: TenantUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> TenantResponse:
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id, Tenant.user_id == current_user.user_id)
    )
    existing_tenant = result.scalar_one_or_none()

    if not existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TENANT_NOT_FOUND
        )

    existing_tenant.cpf = tenant_request.cpf if tenant_request.cpf is not None else existing_tenant.cpf
    existing_tenant.contato = tenant_request.contact if tenant_request.contact is not None else existing_tenant.contato
    existing_tenant.email = tenant_request.email if tenant_request.email is not None else existing_tenant.email
    existing_tenant.nome = tenant_request.name if tenant_request.name is not None else existing_tenant.nome
    existing_tenant.profissao = tenant_request.profession if tenant_request.profession is not None else existing_tenant.profissao
    existing_tenant.estado_civil = tenant_request.marital_status if tenant_request.marital_status is not None else existing_tenant.estado_civil
    existing_tenant.data_nascimento = tenant_request.birth_date if tenant_request.birth_date is not None else existing_tenant.data_nascimento
    existing_tenant.contato_emergencia = tenant_request.emergency_contact if tenant_request.emergency_contact is not None else existing_tenant.contato_emergencia
    existing_tenant.renda = tenant_request.income if tenant_request.income is not None else existing_tenant.renda
    existing_tenant.num_residentes = tenant_request.residents if tenant_request.residents is not None else existing_tenant.num_residentes
    existing_tenant.rua = tenant_request.street if tenant_request.street is not None else existing_tenant.rua
    existing_tenant.bairro = tenant_request.neighborhood if tenant_request.neighborhood is not None else existing_tenant.bairro
    existing_tenant.numero = tenant_request.number if tenant_request.number is not None else existing_tenant.numero
    existing_tenant.cep = tenant_request.zip_code if tenant_request.zip_code is not None else existing_tenant.cep
    existing_tenant.cidade = tenant_request.city if tenant_request.city is not None else existing_tenant.cidade
    existing_tenant.estado = tenant_request.state if tenant_request.state is not None else existing_tenant.estado

    await session.commit()
    await session.refresh(existing_tenant)

    return map_tenant_to_response(existing_tenant)

@router.delete(
    "/tenants/{tenant_id}",
    description="Delete a tenant",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tenant(
    tenant_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id, Tenant.user_id == current_user.user_id)
    )
    existing_tenant = result.scalar_one_or_none()

    if not existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TENANT_NOT_FOUND
        )

    await session.delete(existing_tenant)
    await session.commit()
