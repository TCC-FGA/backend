from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.responses import PDFResponse
from app.controllers.api import deps
from app.models.models import (
    Owner as User,
    Properties,
    Houses,
    PaymentInstallment,
    Expenses,
    Contract,
)
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from weasyprint import HTML  # type: ignore
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd # type: ignore
import uuid
import os


router = APIRouter()


@router.post(
    "/generate-report",
    description="Generate a PDF report",
    status_code=status.HTTP_200_OK,
    response_class=PDFResponse,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Return a PDF file",
        }
    },
)
async def generate_report(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    current_year = datetime.now().year
    try:
        payments_last_year = await session.execute(
            select(func.sum(PaymentInstallment.valor_parcela)).where(
                extract("year", PaymentInstallment.data_vencimento) == current_year,
                PaymentInstallment.fg_pago == True,
                PaymentInstallment.contratos.has(user_id=current_user.user_id),
            )
        )
        total_payments_last_year = float(payments_last_year.scalar() or 0)

        expenses_last_year = await session.execute(
            select(func.sum(Expenses.valor))
            .join(Houses)
            .join(Properties)
            .where(
                extract("year", Expenses.data_despesa) == current_year,
                Properties.user_id == current_user.user_id,
            )
        )
        total_expenses_last_year = float(expenses_last_year.scalar() or 0)

        expenses_by_type = await session.execute(
            select(Expenses.tipo_despesa, func.sum(Expenses.valor))
            .join(Houses)
            .join(Properties)
            .where(
                extract("year", Expenses.data_despesa) == current_year,
                Properties.user_id == current_user.user_id,
            )
            .group_by(Expenses.tipo_despesa)
        )
        expenses_by_type_list = expenses_by_type.all()

        df = pd.DataFrame(expenses_by_type_list, columns=["tipo_despesa", "valor"])
        df["valor"] = df["valor"].astype(float)

        def func_autopct(pct, allvals):
            absolute = int(pct / 100.0 * sum(allvals))
            return "{:.1f}%\n({:d} R$)".format(pct, absolute)

        plt.figure(figsize=(10, 6))
        plt.pie(
            df["valor"],
            labels=[label.capitalize() for label in df["tipo_despesa"]],
            autopct=lambda pct: func_autopct(pct, df["valor"]),
            textprops={"fontsize": 16},
        )
        plt.title("Despesas por Tipo", fontsize=20)
        figure_expenses = f"/tmp/{uuid.uuid4()}.png"
        plt.savefig(figure_expenses)
        plt.close()

        occupancy = await session.execute(
            select(Houses.status, func.count(Houses.id))
            .join(Properties)
            .where(Properties.user_id == current_user.user_id)
            .group_by(Houses.status)
        )
        occupancy_list = occupancy.all()

        df_occupancy = pd.DataFrame(occupancy_list, columns=["status", "count"])
        df_occupancy["count"] = df_occupancy["count"].astype(int)

        total_houses = df_occupancy["count"].sum()

        plt.figure(figsize=(7, 2.5))
        plt.bar(
            df_occupancy["status"],
            df_occupancy["count"],
            color=["green", "red", "orange"],
        )
        plt.title("Taxa de Ocupação dos Imóveis", fontsize=20)
        plt.ylabel("N° Imóveis", fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(range(0, df_occupancy["count"].max() + 1), fontsize=14)

        figure_occupancy = f"/tmp/{uuid.uuid4()}.png"
        plt.savefig(figure_occupancy)
        plt.close()

        income_by_month = await session.execute(
            select(
                extract("month", PaymentInstallment.data_vencimento).label("month"),
                func.sum(PaymentInstallment.valor_parcela).label("income"),
            )
            .join(Contract, Contract.id == PaymentInstallment.contrato_id)
            .join(Houses, Houses.id == Contract.casa_id)
            .join(Properties, Properties.id == Houses.propriedade_id)
            .where(
                extract("year", PaymentInstallment.data_vencimento) == current_year,
                PaymentInstallment.fg_pago == True,
                Properties.user_id == current_user.user_id,
            )
            .group_by("month")
        )
        income_by_month_list = income_by_month.fetchall()

        expense_by_month = await session.execute(
            select(
                extract("month", Expenses.data_despesa).label("month"),
                func.sum(Expenses.valor).label("expense"),
            )
            .join(Houses, Houses.id == Expenses.casa_id)
            .join(Properties, Properties.id == Houses.propriedade_id)
            .where(
                extract("year", Expenses.data_despesa) == current_year,
                Properties.user_id == current_user.user_id,
            )
            .group_by("month")
        )
        expense_by_month_list = expense_by_month.fetchall()

        # Combinar Receita e Despesa em um único DataFrame
        df_income = pd.DataFrame(income_by_month_list, columns=["month", "income"])
        df_expense = pd.DataFrame(expense_by_month_list, columns=["month", "expense"])

        # Mesclar os DataFrames e preencher valores ausentes com zero
        df_income_expense = pd.merge(
            df_income, df_expense, on="month", how="outer"
        ).fillna(0)

        # Converter colunas para float
        df_income_expense["income"] = df_income_expense["income"].astype(float)
        df_income_expense["expense"] = df_income_expense["expense"].astype(float)
        df_income_expense["month"] = df_income_expense["month"].astype(int)

        plt.figure(figsize=(10, 6))
        bar_width = 0.35
        index = df_income_expense["month"]

        plt.bar(
            index - bar_width / 2,
            df_income_expense["income"],
            bar_width,
            label="Receita",
            color="blue",
        )
        plt.bar(
            index + bar_width / 2,
            df_income_expense["expense"],
            bar_width,
            label="Despesa",
            color="red",
        )
        plt.xlabel("Mês", fontsize=16)
        plt.ylabel("Valor (R$)", fontsize=16)
        plt.title("Receita e Despesa por Mês", fontsize=22)
        plt.xticks(
            index,
            [str(int(month)) for month in df_income_expense["month"]],
            fontsize=16,
        )
        plt.yticks(fontsize=16)
        plt.legend(fontsize=14)

        figure_income_expense = f"/tmp/{uuid.uuid4()}.png"
        plt.savefig(figure_income_expense)
        plt.close()

        # Identificar o tipo de despesa com maior valor
        if not df.empty:
            maior_tipo_despesa = df.loc[df["valor"].idxmax(), "tipo_despesa"]
        else:
            maior_tipo_despesa = "N/A"

        # Identificar o status de imóvel mais comum
        if not df_occupancy.empty:
            status_mais_comum = df_occupancy.loc[
                df_occupancy["count"].idxmax(), "status"
            ]
        else:
            status_mais_comum = "N/A"

        html_template = f"""
        <html>
        <head>
            <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #333; }}
            img {{ width: 100%; max-width: 600px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #333; padding: 8px; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>Relatório e-Aluguel</h1>
            <h2>Informações Financeiras</h2>
            <p>Este relatório apresenta uma análise detalhada das receitas e despesas do último ano, bem como insights sobre a distribuição de despesas por tipo e a taxa de ocupação dos imóveis.</p>

            <h3>Gráfico de Despesas por Tipo</h3>
            <img src="file://{figure_expenses}" alt="Gráfico de Despesas por Tipo">
            
            <h3>Taxa de Ocupação dos Imóveis</h3>
            <img src="file://{figure_occupancy}" alt="Taxa de Ocupação dos Imóveis">
            <p>Total de Imóveis: <b>{total_houses}</b></p>

            <h3>Receita e Despesa por Mês</h3>
            <img src="file://{figure_income_expense}" alt="Receita e Despesa por Mês">

            <h3>Resumo</h3>
            <p>No último ano, a receita totalizou <b>{total_payments_last_year:.2f} R$</b>, enquanto as despesas foram de <b>{total_expenses_last_year:.2f} R$</b>, resultando em um saldo <b>{(total_payments_last_year - total_expenses_last_year):.2f}</b> R$.</p>
            <p>O tipo de despesa com maior impacto foi <b>{maior_tipo_despesa.capitalize()}</b>.</p>
            <p>A maior parte dos imóveis está com o status <b>{status_mais_comum.capitalize()}</b>.</p>

            <h2>Informações Adicionais</h2>

            <h3>Receita por Mês</h3>
            <table>
                <tr>
                    <th>Mês</th>
                    <th>Receita (R$)</th>
                </tr>
                {"".join(f"<tr><td>{row.month}</td><td>{row.income:.2f}</td></tr>" for row in income_by_month_list)}
            </table>

            <h3>Despesa por Mês</h3>
            <table>
                <tr>
                    <th>Mês</th>
                    <th>Despesa (R$)</th>
                </tr>
                {"".join(f'<tr><td>{row.month}</td><td>{row.expense:.2f}</td></tr>' for row in expense_by_month_list)}
            </table>
            <br>
            <p>Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>


        </body>
        </html>
        """
        pdf = HTML(string=html_template).write_pdf()

        with open ("report.pdf", "wb") as f:
            f.write(pdf)    

        os.remove(figure_expenses)
        os.remove(figure_occupancy)
        os.remove(figure_income_expense)

        return PDFResponse(content=pdf, filename="report.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {e} Cadastre despesas e receitas para o ano corrente.")
