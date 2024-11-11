from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.schemas.map_responses import map_payment_installment_to_response
from app.schemas.responses import PaymentInstallmentResponse

from app.schemas.requests import PaymentInstallmentUpdateRequest
from app.models.models import PaymentInstallment
from app.models.models import Contract
from app.models.models import Owner as User

router = APIRouter()


@router.post(
    "/payment_installment/{contract_id}",
    response_model=list[PaymentInstallmentResponse],
    description="Create a new payment installment for the contract",
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_installment(
    contract_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[PaymentInstallmentResponse]:

    result = await session.execute(
        select(Contract).where(
            Contract.id == contract_id, Contract.user_id == current_user.user_id
        )
    )
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.CONTRACT_NOT_FOUND,
        )

    contract_duration = (contract.data_fim.year - contract.data_inicio.year) * 12 + (
        contract.data_fim.month - contract.data_inicio.month
    )

    if contract_duration < 1:
        raise HTTPException(
            status_code=400, detail=api_messages.CONTRACT_DURATION_ERROR
        )

    try:
        parcelas = []
        data_inicio = contract.data_inicio.replace(day=contract.dia_vencimento)
        valor_parcela = Decimal(contract.valor_base)

        for i in range(contract_duration):
            data_vencimento_parcela = data_inicio + relativedelta(months=i + 1)

            if contract.taxa_reajuste == "IGPM" and i > 0 and i % 12 == 0:
                valor_parcela *= Decimal("1.045")

            new_payment_installment = PaymentInstallment(
                contrato_id=contract.id,
                valor_parcela=valor_parcela.quantize(Decimal("0.01")),
                fg_pago=False,
                tipo_pagamento=None,
                data_vencimento=data_vencimento_parcela,
                data_pagamento=None,
            )

            parcelas.append(new_payment_installment)

        session.add_all(parcelas)
        await session.commit()
        for parcela in parcelas:
            await session.refresh(parcela)

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"{api_messages.ERROR_CREATING_PAYMENT_INSTALLMENT}: {str(e)}",
        )

    return [map_payment_installment_to_response(parcela) for parcela in parcelas]


@router.get(
    "/payment_installment/{contract_id}",
    response_model=list[PaymentInstallmentResponse],
    description="Get all payment installments for the contract",
    status_code=status.HTTP_200_OK,
)
async def get_payment_installments(
    contract_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> list[PaymentInstallmentResponse]:

    result = await session.execute(
        select(Contract).where(
            Contract.id == contract_id, Contract.user_id == current_user.user_id
        )
    )
    contract = result.scalar_one_or_none()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.CONTRACT_NOT_FOUND,
        )

    payment = await session.execute(
        select(PaymentInstallment).where(PaymentInstallment.contrato_id == contract_id)
    )
    payment_installments = payment.scalars().all()

    return [
        map_payment_installment_to_response(payment_installment)
        for payment_installment in payment_installments
    ]


@router.patch(
    "/payment_installment/{payment_installment_id}",
    response_model=PaymentInstallmentResponse,
    description="Update a payment installment",
    status_code=status.HTTP_200_OK,
)
async def update_payment_installment(
    payment_installment_id: int,
    payment_installment: PaymentInstallmentUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> PaymentInstallmentResponse:

    result = await session.execute(
        select(PaymentInstallment).where(
            PaymentInstallment.id == payment_installment_id,
            PaymentInstallment.contratos.has(user_id=current_user.user_id),
        )
    )
    existing_payment_installment = result.scalar_one_or_none()

    if not existing_payment_installment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.PAYMENT_INSTALLMENT_NOT_FOUND,
        )

    existing_payment_installment.fg_pago = (
        payment_installment.fg_paid
        if payment_installment.fg_paid is not None
        else existing_payment_installment.fg_pago
    )
    existing_payment_installment.tipo_pagamento = (
        payment_installment.payment_type
        if payment_installment.payment_type is not None
        else existing_payment_installment.tipo_pagamento  # type: ignore
    )
    existing_payment_installment.data_pagamento = (
        payment_installment.payment_date
        if payment_installment.payment_date is not None
        else existing_payment_installment.data_pagamento
    )

    await session.commit()
    await session.refresh(existing_payment_installment)

    return map_payment_installment_to_response(existing_payment_installment)
