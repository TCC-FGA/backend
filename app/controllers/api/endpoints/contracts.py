from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.schemas.map_responses import map_contract_to_response
from app.schemas.responses import ContractResponse
from app.schemas.requests import ContractCreateRequest
from app.models.models import Contract
from app.models.models import Owner as User

router = APIRouter()

@router.get(
    "/contracts",
    response_model=list[ContractResponse],
    description="Get all contracts for the current user",
)
async def get_contracts(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[ContractResponse]:
    result = await session.execute(
        select(Contract).filter(Contract.user_id == current_user.user_id)
    )
    contracts = result.scalars().all()

    if not contracts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.CONTRACT_NOT_FOUND,
        )

    return [map_contract_to_response(contract) for contract in contracts]

@router.get(
    "/contracts/{contract_id}",
    response_model=ContractResponse,
    description="Get a contract by its id",
)
async def get_contract(
    contract_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> ContractResponse:
    result = await session.execute(
        select(Contract).filter(
            Contract.id == contract_id, Contract.user_id == current_user.user_id
        )
    )
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.CONTRACT_NOT_FOUND,
        )

    return map_contract_to_response(contract)

@router.post(
    "/contracts",
    response_model=ContractResponse,
    description="Create a contract",
    status_code=status.HTTP_201_CREATED,
)
async def create_contract(
    contract: ContractCreateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> ContractResponse:
    
    new_contract = Contract(
        valor_caucao=contract.deposit_value,
        data_inicio=contract.start_date,
        data_fim=contract.end_date,
        valor_base=contract.base_value,
        dia_vencimento=contract.due_date,
        taxa_reajuste=contract.reajustment_rate,
        casa_id=contract.house_id,
        template_id=contract.template_id,
        inquilino_id=contract.tenant_id,
        user_id=current_user.user_id,
    )

    session.add(new_contract)
    await session.commit()
    await session.refresh(new_contract)

    return map_contract_to_response(new_contract)

@router.delete(
    "/contracts/{contract_id}",
    description="Delete a contract by its id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contract(
    contract_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    result = await session.execute(
        select(Contract).filter(
            Contract.id == contract_id, Contract.user_id == current_user.user_id
        )
    )
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.CONTRACT_NOT_FOUND,
        )

    await session.delete(contract)
    await session.commit()
    return None