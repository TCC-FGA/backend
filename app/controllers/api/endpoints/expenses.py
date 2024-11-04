from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.schemas.map_responses import map_expense_to_response
from app.schemas.responses import ExpenseResponse
from app.schemas.requests import ExpenseCreateRequest, ExpenseUpdateRequest
from app.models.models import Expenses
from app.models.models import Owner as User

router = APIRouter()


@router.get(
    "/expenses/{house_id}",
    response_model=list[ExpenseResponse],
    description="Get all expenses by house id",
)
async def get_expenses(
    house_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[ExpenseResponse]:
    result = await session.execute(
        select(Expenses).filter(Expenses.casa_id == house_id)
    )
    expenses = result.scalars().all()

    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.EXPENSE_NOT_FOUND,
        )

    return [map_expense_to_response(expense) for expense in expenses]


@router.post(
    "/expenses/{house_id}",
    response_model=ExpenseResponse,
    description="Create a new expense",
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    house_id: int,
    expense_data: ExpenseCreateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> ExpenseResponse:

    new_expense = Expenses(
        tipo_despesa=expense_data.expense_type,
        valor=expense_data.value,
        data_despesa=expense_data.expense_date,
        casa_id=house_id,
    )

    session.add(new_expense)
    await session.commit()
    await session.refresh(new_expense)

    return map_expense_to_response(new_expense)


@router.patch(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    description="Update an expense",
    status_code=status.HTTP_200_OK,
)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> ExpenseResponse:
    result = await session.execute(select(Expenses).filter(Expenses.id == expense_id))
    existing_expense = result.scalar_one_or_none()

    if not existing_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.EXPENSE_NOT_FOUND,
        )

    existing_expense.tipo_despesa = (
        expense_data.expense_type
        if expense_data.expense_type is not None
        else existing_expense.tipo_despesa #type: ignore
    )
    existing_expense.valor = (
        expense_data.value if expense_data.value is not None else existing_expense.valor
    )
    existing_expense.data_despesa = (
        expense_data.expense_date
        if expense_data.expense_date is not None
        else existing_expense.data_despesa
    )

    await session.commit()
    await session.refresh(existing_expense)

    return map_expense_to_response(existing_expense)

@router.delete(
    "/expenses/{expense_id}",
    description="Delete an expense",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    result = await session.execute(
        select(Expenses).filter(Expenses.id == expense_id)
    )
    existing_expense = result.scalar_one_or_none()

    if not existing_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.EXPENSE_NOT_FOUND,
        )

    await session.delete(existing_expense)
    await session.commit()