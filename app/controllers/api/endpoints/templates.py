from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.schemas.map_responses import map_template_to_response
from app.schemas.responses import TemplateResponse
from app.schemas.requests import TemplateCreateRequest, TemplateUpdateRequest
from app.models.models import Template
from app.models.models import Owner as User

router = APIRouter()


@router.get(
    "/templates",
    response_model=list[TemplateResponse],
    description="Get all templates for the current user",
)
async def get_templates(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[TemplateResponse]:
    result = await session.execute(
        select(Template).filter(Template.user_id == current_user.user_id)
    )
    templates = result.scalars().all()

    if not templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TEMPLATE_NOT_FOUND,
        )

    return [map_template_to_response(template) for template in templates]


@router.get(
    "/templates/{template_id}",
    response_model=TemplateResponse,
    description="Get a template by its id",
)
async def get_template(
    template_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> TemplateResponse:
    result = await session.execute(
        select(Template).filter(
            Template.id == template_id, Template.user_id == current_user.user_id
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TEMPLATE_NOT_FOUND,
        )

    return map_template_to_response(template)


@router.post(
    "/templates",
    response_model=TemplateResponse,
    description="Create a template",
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    template_data: TemplateCreateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> TemplateResponse:

    new_template = Template(
        nome_template=template_data.template_name,
        descricao=template_data.description,
        garagem=template_data.garage,
        garantia=template_data.warranty,
        animais=template_data.animals,
        sublocacao=template_data.sublease,
        tipo_contrato=template_data.contract_type,
        user_id=current_user.user_id,
    )
    session.add(new_template)
    await session.commit()
    await session.refresh(new_template)

    return map_template_to_response(new_template)


@router.patch(
    "/templates/{template_id}",
    response_model=TemplateResponse,
    description="Update a template for the current user",
    status_code=status.HTTP_200_OK,
)
async def update_template(
    template_id: int,
    template_data: TemplateUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> TemplateResponse:

    result = await session.execute(
        select(Template).where(
            Template.id == template_id, Template.user_id == current_user.user_id
        )
    )
    existing_template = result.scalar_one_or_none()

    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TEMPLATE_NOT_FOUND,
        )

    existing_template.nome_template = (
        template_data.template_name
        if template_data.template_name is not None
        else existing_template.nome_template
    )
    existing_template.descricao = (
        template_data.description
        if template_data.description is not None
        else existing_template.descricao
    )
    existing_template.garagem = (
        template_data.garage
        if template_data.garage is not None
        else existing_template.garagem
    )
    existing_template.garantia = (
        template_data.warranty
        if template_data.warranty is not None
        else existing_template.garantia # type: ignore
    )
    existing_template.animais = (
        template_data.animals
        if template_data.animals is not None
        else existing_template.animais
    )
    existing_template.sublocacao = (
        template_data.sublease
        if template_data.sublease is not None
        else existing_template.sublocacao
    )
    existing_template.tipo_contrato = (
        template_data.contract_type
        if template_data.contract_type is not None
        else existing_template.tipo_contrato # type: ignore
    )

    session.add(existing_template)
    await session.commit()
    await session.refresh(existing_template)

    return map_template_to_response(existing_template)


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a template by its id",
)
async def delete_template(
    template_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    result = await session.execute(
        select(Template).where(
            Template.id == template_id, Template.user_id == current_user.user_id
        )
    )
    existing_template = result.scalar_one_or_none()

    if not existing_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.TEMPLATE_NOT_FOUND,
        )

    await session.delete(existing_template)
    await session.commit()
