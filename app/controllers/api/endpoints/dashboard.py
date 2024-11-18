from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import requests
import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.core.config import get_settings
from app.models.models import Contract, Owner as User
from app.models.models import Properties
from app.models.models import Houses
from app.models.models import Tenant
from app.models.models import PaymentInstallment
from app.models.models import Expenses

from app.schemas.responses import DashboardResponse

router = APIRouter()


@router.get(
    "/dashboard/totals",
    response_model=DashboardResponse.Totals,
    description="Get all totals",
    status_code=status.HTTP_200_OK,
)
async def get_dashboard_totals(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> DashboardResponse.Totals:
    properties_count = await session.execute(
        select(func.count(Properties.id)).where(
            Properties.user_id == current_user.user_id
        )
    )
    houses_count = await session.execute(
        select(func.count(Houses.id))
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Properties.user_id == current_user.user_id)
    )
    tenants_count = await session.execute(
        select(func.count(Tenant.id)).where(Tenant.user_id == current_user.user_id)
    )

    total_properties = properties_count.scalar() or 0
    total_houses = houses_count.scalar() or 0
    total_tenants = tenants_count.scalar() or 0

    return DashboardResponse.Totals(
        total_properties=total_properties,
        total_houses=total_houses,
        total_tenants=total_tenants,
    )


@router.get(
    "/dashboard/houses-availability",
    response_model=DashboardResponse.HousesAvailability,
    description="Get all houses availability",
    status_code=status.HTTP_200_OK,
)
async def get_dashboard_houses_availability(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> DashboardResponse.HousesAvailability:
    rented_count = await session.execute(
        select(func.count(Houses.id))
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Properties.user_id == current_user.user_id, Houses.status == "alugada")
    )
    available_count = await session.execute(
        select(func.count(Houses.id))
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Properties.user_id == current_user.user_id, Houses.status == "vaga")
    )
    maintenance_count = await session.execute(
        select(func.count(Houses.id))
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Properties.user_id == current_user.user_id, Houses.status == "reforma")
    )

    total_rented = rented_count.scalar() or 0
    total_available = available_count.scalar() or 0
    total_maintenance = maintenance_count.scalar() or 0

    return DashboardResponse.HousesAvailability(
        total_rented=total_rented,
        total_available=total_available,
        total_maintenance=total_maintenance,
    )


@router.get(
    "/dashboard/cash-flow",
    response_model=DashboardResponse.CashFlow,
    description="Get cash flow for the current month",
    status_code=status.HTTP_200_OK,
)
async def get_dashboard_cash_flow(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> DashboardResponse.CashFlow:
    current_month = date.today().month
    current_year = date.today().year

    income_query = await session.execute(
        select(func.sum(PaymentInstallment.valor_parcela)).where(
            extract("month", PaymentInstallment.data_vencimento) == current_month,
            extract("year", PaymentInstallment.data_vencimento) == current_year,
            PaymentInstallment.fg_pago == True,
            PaymentInstallment.contratos.has(user_id=current_user.user_id),
        )
    )

    total_monthly_income = income_query.scalar() or 0.0

    expenses_query = await session.execute(
        select(func.sum(Expenses.valor)).where(
            extract("month", Expenses.data_despesa) == current_month,
            extract("year", Expenses.data_despesa) == current_year,
            Expenses.casas.has(Properties.user_id == current_user.user_id),
        )
    )
    total_monthly_expenses = expenses_query.scalar() or 0.0

    total_monthly_income = float(total_monthly_income)
    total_monthly_expenses = float(total_monthly_expenses)

    total_profit_monthly = total_monthly_income - total_monthly_expenses

    return DashboardResponse.CashFlow(
        total_monthly_income=round(total_monthly_income, 2),
        total_monthly_expenses=round(total_monthly_expenses, 2),
        total_profit_monthly=round(total_profit_monthly, 2),
    )


@router.get(
    "/dashboard/payment-status",
    response_model=DashboardResponse.PaymentStatus,
    description="Get payment status for the current month",
    status_code=status.HTTP_200_OK,
)
async def get_dashboard_payment_status(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> DashboardResponse.PaymentStatus:
    current_month = date.today().month
    current_year = date.today().year
    current_day = date.today().day

    total_payments_query = await session.execute(
        select(func.count(PaymentInstallment.id)).where(
            extract("month", PaymentInstallment.data_vencimento) == current_month,
            extract("year", PaymentInstallment.data_vencimento) == current_year,
            PaymentInstallment.contratos.has(user_id=current_user.user_id),
        )
    )
    total_payments = total_payments_query.scalar() or 0

    paid_payments_query = await session.execute(
        select(func.count(PaymentInstallment.id)).where(
            extract("month", PaymentInstallment.data_vencimento) == current_month,
            extract("year", PaymentInstallment.data_vencimento) == current_year,
            PaymentInstallment.fg_pago == True,
            PaymentInstallment.contratos.has(user_id=current_user.user_id),
        )
    )
    paid_payments = paid_payments_query.scalar() or 0

    overdue_payments_query = await session.execute(
        select(func.count(PaymentInstallment.id)).where(
            extract("month", PaymentInstallment.data_vencimento) == current_month,
            extract("year", PaymentInstallment.data_vencimento) == current_year,
            PaymentInstallment.fg_pago == False,
            PaymentInstallment.data_vencimento < date.today(),
            PaymentInstallment.contratos.has(user_id=current_user.user_id),
        )
    )
    overdue_payments = overdue_payments_query.scalar() or 0

    pending_payments_query = await session.execute(
        select(func.count(PaymentInstallment.id)).where(
            extract("month", PaymentInstallment.data_vencimento) == current_month,
            extract("year", PaymentInstallment.data_vencimento) == current_year,
            PaymentInstallment.fg_pago == False,
            PaymentInstallment.data_vencimento >= date.today(),
            PaymentInstallment.contratos.has(user_id=current_user.user_id),
        )
    )
    pending_payments = pending_payments_query.scalar() or 0

    total_payments = total_payments
    paid_percentage = (paid_payments / total_payments) * 100 if total_payments > 0 else 0.0
    overdue_percentage = (overdue_payments / total_payments) * 100 if total_payments > 0 else 0.0
    pending_percentage = (pending_payments / total_payments) * 100 if total_payments > 0 else 0.0

    return DashboardResponse.PaymentStatus(
        total_monthly_paid=round(paid_percentage, 2),
        total_monthly_overdue=round(overdue_percentage, 2),
        total_monthly_pending=round(pending_percentage, 2),
    )

ONESIGNAL_APP_ID = "1243b543-9212-4940-84d8-70af01639081"
ONESIGNAL_API_URL = "https://onesignal.com/api/v1/notifications"
ONESIGNAL_API_KEY = get_settings().security.onesignal_api_key.get_secret_value()

def send_notification(user_id: str, tenant_name: str, installment_id: int, due_date: date, amount: float):
    headers = {
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "app_id": ONESIGNAL_APP_ID,
        "target_channel": "push",
        "headings": {"en": "Parcela Vencida", "es": "Cuota Vencida", "pt": "Parcela Vencida"},
        "contents": {
            "en": f"O inquilino {tenant_name} tem uma parcela vencida com vencimento em {due_date}. Valor: {amount}",
            "es": f"El inquilino {tenant_name} tiene una cuota vencida con fecha de vencimiento {due_date}. Monto: {amount}",
            "pt": f"O inquilino {tenant_name} tem uma parcela vencida com vencimento em {due_date}. Valor: {amount}"
        },
        "filters": [
            {"field": "tag", "key": "userId", "relation": "=", "value": user_id}
        ]
    }
    response = requests.post(ONESIGNAL_API_URL, headers=headers, json=body)
    if response.status_code == 200:
        print(f"Notification sent successfully for User ID: {user_id}")
    else:
        print(f"Failed to send notification for User ID: {user_id}. Status Code: {response.status_code}, Response: {response.text}")

@router.get(
    "/notifications/overdue-installments",
    description="Get overdue installments for all users",
    status_code=status.HTTP_200_OK,
)
async def get_overdue_installments(
    session: AsyncSession = Depends(deps.get_session),
):
    current_month = date.today().month
    current_year = date.today().year

    overdue_installments_query = await session.execute(
        select(PaymentInstallment).where(
            extract("month", PaymentInstallment.data_vencimento) == current_month,
            extract("year", PaymentInstallment.data_vencimento) == current_year,
            PaymentInstallment.fg_pago == False,
            PaymentInstallment.data_vencimento < date.today(),
        )
    )
    overdue_installments = overdue_installments_query.scalars().all()

    if not overdue_installments:
        print("No overdue installments for the current month.")
    else:
        for installment in overdue_installments:
            contract_query = await session.execute(
                select(Contract).where(Contract.id == installment.contrato_id)
            )
            contract = contract_query.scalar_one_or_none()
            if contract:
                tenant_query = await session.execute(
                    select(Tenant).where(Tenant.id == contract.inquilino_id)
                )
                tenant = tenant_query.scalar_one_or_none()
                if tenant:
                    user_query = await session.execute(
                        select(User).where(User.user_id == tenant.user_id)
                    )
                    user = user_query.scalar_one_or_none()
                    if user:
                        print(f"User: {user.nome}, Tenant: {tenant.nome}, Installment ID: {installment.id}, Due Date: {installment.data_vencimento}, Amount: {installment.valor_parcela}")
                        send_notification(user.user_id, tenant.nome, installment.id, installment.data_vencimento, installment.valor_parcela)

    return {"message": "Overdue installments check completed."}