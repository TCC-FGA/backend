from datetime import date
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, PageBreak, Table, TableStyle
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Image,
)
import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.schemas.map_responses import map_inspection_to_response
from app.schemas.responses import InspectionResponse
from app.schemas.requests import InspectionCreateRequest
from app.models.models import Contract, Props
from app.models.models import Houses
from app.models.models import Tenant
from app.models.models import Properties
from app.models.models import Inspection
from app.models.models import Owner as User
from app.storage.gcs import GCStorage


router = APIRouter()


@router.get(
    "/inspection/{contract_id}",
    response_model=InspectionResponse,
    description="Get an inspection by its contract id",
    status_code=status.HTTP_200_OK,
)
async def get_inspection(
    contract_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> InspectionResponse:
    result = await session.execute(
        select(Inspection)
        .join(Contract, Inspection.contrato_id == Contract.id)
        .where(Contract.id == contract_id)
        .where(Contract.user_id == current_user.user_id)
    )
    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.INSPECTION_NOT_FOUND,
        )

    return map_inspection_to_response(inspection)


@router.post(
    "/inspection/{contract_id}",
    response_model=InspectionResponse,
    description="Create a new inspection for a contract",
    status_code=status.HTTP_201_CREATED,
)
async def create_inspection(
    contract_id: int,
    inspection_data: InspectionCreateRequest = Depends(InspectionCreateRequest.as_form),
    inspection_photos: list[UploadFile] = File(
        None, description="Photos from the inspection"
    ),
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> InspectionResponse:
    contract_result = await session.execute(
        select(Contract, Properties, Tenant)
        .join(Houses, Contract.casa_id == Houses.id)
        .join(Properties, Houses.propriedade_id == Properties.id)
        .join(Tenant, Contract.inquilino_id == Tenant.id)
        .where(Contract.id == contract_id)
        .where(Contract.user_id == current_user.user_id)
        .where(Properties.user_id == current_user.user_id)
        .where(Tenant.user_id == current_user.user_id)
    )
    contract = contract_result.one_or_none()
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.CONTRACT_NOT_FOUND,
        )

    existing_inspection_result = await session.execute(
        select(Inspection).where(Inspection.contrato_id == contract_id)
    )
    existing_inspection = existing_inspection_result.scalar_one_or_none()

    contract, property, tenant = contract

    pdf_created = create_inspection_pdf(
        inspection_data,
        current_user,
        tenant,
        property,
        inspection_photos,
        f"/tmp/vistoria_{contract_id}.pdf",
    )

    key = await session.execute(select(Props.column).limit(1))
    key_response = key.scalar_one_or_none()
    gcs = GCStorage(key_response)
    with open(pdf_created, "rb") as file:
        pdf_vistoria = gcs.upload_content(file, "pdf")

    if existing_inspection:
        existing_inspection.pdf_vistoria = pdf_vistoria
        existing_inspection.data_vistoria = inspection_data.data_vistoria

        inspection = existing_inspection

    else:
        inspection = Inspection(
            contrato_id=contract_id,
            pdf_vistoria=pdf_vistoria,
            data_vistoria=inspection_data.data_vistoria,
        )

    session.add(inspection)
    await session.commit()
    await session.refresh(inspection)

    return map_inspection_to_response(inspection)


@router.patch(
    "/inspection/{inspection_id}",
    response_model=InspectionResponse,
    description="Submit an inspection by its id",
    status_code=status.HTTP_200_OK,
)
async def submit_inspection(
    inspection_id: int,
    inspection_pdf: UploadFile = File(None, description="PDF signed by the parties"),
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> InspectionResponse:
    result = await session.execute(
        select(Inspection)
        .join(Contract, Inspection.contrato_id == Contract.id)
        .where(Inspection.id == inspection_id)
        .where(Contract.user_id == current_user.user_id)
    )
    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.INSPECTION_NOT_FOUND,
        )

    key = await session.execute(select(Props.column).limit(1))
    key_response = key.scalar_one_or_none()
    file_path = GCStorage(key_response).upload_file(inspection_pdf, "pdf")

    inspection.pdf_assinado = file_path if file_path else inspection.pdf_assinado

    await session.commit()
    await session.refresh(inspection)

    return map_inspection_to_response(inspection)


def create_inspection_pdf(
    inspection_data: InspectionCreateRequest,
    owner: User,
    tenant: Tenant,
    property: Properties,
    inspection_photos: list[UploadFile] | None,
    file_path: str,
) -> str:
    doc = BaseDocTemplate(file_path, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"], alignment=1, fontSize=14, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Heading2"], alignment=1, fontSize=12, spaceAfter=10
    )
    text_style = styles["BodyText"]
    text_style.leading = 14
    signatures_style = ParagraphStyle(
        "Signature", parent=styles["BodyText"], alignment=1, leading=20
    )

    frame = Frame(50, 50, width - 100, height - 100, showBoundary=0)
    template = PageTemplate(id="main_template", frames=[frame], onPage=add_page_number)
    doc.addPageTemplates([template])

    content = [
        Paragraph("TERMO DE VISTORIA INICIAL DO IMÓVEL", title_style),
        Paragraph("CONTRATO DE LOCAÇÃO", subtitle_style),
        Paragraph(
            f"LOCADOR: {owner.nome}, inscrito no CPF sob nº {owner.cpf}, e-mail {owner.email}, residente e domiciliado na rua {owner.rua}, {owner.numero}, no bairro {owner.bairro}, {owner.cep} em {owner.cidade}/{owner.estado}.",
            text_style,
        ),
        Paragraph(
            f"LOCATÁRIO: {tenant.nome}, {tenant.estado_civil}, {tenant.profissao} inscrito no CPF sob nº {tenant.cpf}, e-mail {tenant.email}, residente e domiciliado na rua {tenant.rua}, {tenant.numero}, no bairro {tenant.bairro}, {tenant.cep} em {tenant.cidade}/{tenant.estado}.",
            text_style,
        ),
        Paragraph(
            f"IMÓVEL OBJETO DA LOCAÇÃO: Imóvel situado na rua {property.rua}, no bairro {property.bairro}, n° {property.numero}, em {property.cidade}/{property.estado}.",
            text_style,
        ),
        Paragraph(
            "Firmam por meio do presente o termo de vistoria e entrega das chaves ao locatário para início na data de hoje da vigência do contrato de locação.",
            text_style,
        ),
        Paragraph(
            "O presente termo é parte integrante do contrato de locação celebrado entre as partes.",
            text_style,
        ),
        Paragraph(
            "Pelo presente, declaram as partes, que o o imóvel acima indicado se encontra em bom estado de conservação, com todos os acessórios em prefeito estado de funcionamento e conservação, sendo que dessa forma o LOCATÁRIO se compromete a devolvê-lo no mesmo estado, findo o prazo contratual, independente de vistoria final.",
            text_style,
        ),
        Paragraph("O imóvel está inspecionado conforme os itens abaixo:", text_style),
        Spacer(1, 12),
    ]

    if inspection_data.pintura:
        content.append(
            Paragraph(
                f"1) PINTURA: {inspection_data.pintura.estado_pintura.value}, Tipo: {inspection_data.pintura.tipo_tinta.value}, Cor: {inspection_data.pintura.cor or 'Não especificada'}.",
                text_style,
            )
        )
    if inspection_data.acabamento:
        content.append(
            Paragraph(
                f"2) ACABAMENTO: {inspection_data.acabamento.condicao or 'Não especificado'}, Observações: {inspection_data.acabamento.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.eletrica:
        content.append(
            Paragraph(
                f"3) ELÉTRICA: {inspection_data.eletrica.condicao.value}, Observações: {inspection_data.eletrica.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.trincos_fechaduras:
        content.append(
            Paragraph(
                f"4) TRINCOS e FECHADURAS: {inspection_data.trincos_fechaduras.condicao or 'Não especificado'}, Observações: {inspection_data.trincos_fechaduras.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.piso_azulejos:
        content.append(
            Paragraph(
                f"5) PISOS E AZULEJOS: {inspection_data.piso_azulejos.condicao or 'Não especificado'}, Observações: {inspection_data.piso_azulejos.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.vidracaria_janelas:
        content.append(
            Paragraph(
                f"6) VIDRAÇAS e JANELAS: {inspection_data.vidracaria_janelas.condicao or 'Não especificado'}, Observações: {inspection_data.vidracaria_janelas.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.telhado:
        content.append(
            Paragraph(
                f"7) TELHADO: {inspection_data.telhado.condicao or 'Não especificado'}, Observações: {inspection_data.telhado.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.hidraulica:
        content.append(
            Paragraph(
                f"8) HIDRÁULICA: {inspection_data.hidraulica.condicao or 'Não especificado'}, Observações: {inspection_data.hidraulica.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.mobilia:
        content.append(
            Paragraph(
                f"9) MOBILIA: Observações: {inspection_data.mobilia.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )
    if inspection_data.chave:
        content.append(
            Paragraph(
                f"10) CHAVES: Número: {inspection_data.chave.numero or 'Não especificado'}, Observações: {inspection_data.chave.observacoes or 'Nenhuma'}.",
                text_style,
            )
        )

    content.append(
        Paragraph(
            f"Qualquer impugnação ao presente laudo deverá ser comunicada ao LOCADOR por escrito, dentro de 07 (sete) dias a contar da data da assinatura deste. destinado ao e-mail {owner.email} A falta de comunicação implica em aceitação de vistoria realizada nos termos descritos acima",
            text_style,
        )
    )
    content.append(Spacer(1, 12))

    if inspection_photos:
        content.append(PageBreak())  # Adiciona uma quebra de página antes das fotos
        fotos_por_linha = 2
        espaco_entre_fotos = 20
        largura_foto = (
            width - 50 - espaco_entre_fotos * (fotos_por_linha - 1)
        ) / fotos_por_linha
        altura_foto = 150
        photo_table_data = []
        photo_row = []

        for i, photo in enumerate(inspection_photos):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(photo.file.read())
                tmp.flush()
                photo_row.append(
                    Image(tmp.name, width=largura_foto, height=altura_foto)
                )

            if (i + 1) % fotos_por_linha == 0:
                photo_table_data.append(photo_row)
                photo_row = []
            else:
                photo_row.append(Spacer(1, espaco_entre_fotos))  # type: ignore

        if photo_row:
            photo_table_data.append(photo_row)

        photo_table = Table(
            photo_table_data,
            colWidths=[largura_foto, espaco_entre_fotos] * fotos_por_linha,
        )
        photo_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        content.append(photo_table)

    content.append(PageBreak())
    content.append(Spacer(1, 150))
    content.extend(
        [
            Paragraph("____________________________________", signatures_style),
            Paragraph("Locatário", signatures_style),
            Paragraph("____________________________________", signatures_style),
            Paragraph("Locador", signatures_style),
            Paragraph("____________________________________", signatures_style),
            Paragraph("Testemunha", signatures_style),
            Spacer(1, 50),
            Paragraph("Local: ________________________", signatures_style),
            Paragraph("Data: __/__/____", signatures_style),
        ]
    )

    doc.build(content)

    return file_path


def add_page_number(canvas, doc):
    canvas.setFont("Helvetica", 10)
    page_num_text = f"Página {doc.page}"
    canvas.drawString(doc.pagesize[0] - 100, 15, page_num_text)
