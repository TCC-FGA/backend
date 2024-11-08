from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from weasyprint import HTML  # type: ignore
from num2words import num2words  # type: ignore

import app.controllers.api.api_messages as api_messages
from app.controllers.api import deps
from app.schemas.map_responses import map_contract_to_response
from app.schemas.responses import ContractResponse, PDFResponse
from app.schemas.requests import ContractCreateRequest
from app.models.models import Contract, Props
from app.models.models import Houses
from app.models.models import Tenant
from app.models.models import Properties
from app.models.models import Template
from app.models.models import Inspection
from app.models.models import Guarantor
from app.models.models import Owner as User
from app.storage.gcs import GCStorage


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
        select(Contract, Houses, Tenant)
        .join(Houses, Contract.casa_id == Houses.id)
        .join(Properties, Houses.propriedade_id == Properties.id)
        .join(Tenant, Contract.inquilino_id == Tenant.id)
        .where(Contract.user_id == current_user.user_id)
        .where(Properties.user_id == current_user.user_id)
        .where(Tenant.user_id == current_user.user_id)
    )

    contracts = result.all()

    return [
        map_contract_to_response(contract, house, tenant)
        for contract, house, tenant in contracts
    ]


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

    house_result = await session.execute(
        select(Houses)
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Houses.id == contract.casa_id)
        .where(Properties.user_id == current_user.user_id)
    )
    house = house_result.scalar_one_or_none()
    if not house:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.FORBIDDEN_HOUSE,
        )

    tenant_result = await session.execute(
        select(Tenant)
        .where(Tenant.id == contract.inquilino_id)
        .where(Tenant.user_id == current_user.user_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.FORBIDDEN_TENANT,
        )

    return map_contract_to_response(contract, house, tenant)


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
    house_result = await session.execute(
        select(Houses)
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Houses.id == contract.house_id)
        .where(Properties.user_id == current_user.user_id)
    )
    house = house_result.scalar_one_or_none()

    if not house:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.FORBIDDEN_HOUSE,
        )

    tenant_result = await session.execute(
        select(Tenant)
        .where(Tenant.id == contract.tenant_id)
        .where(Tenant.user_id == current_user.user_id)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.FORBIDDEN_TENANT,
        )

    new_contract = Contract(
        valor_caucao=contract.deposit_value,
        data_inicio=contract.start_date,
        data_fim=contract.end_date,
        valor_base=contract.base_value,
        dia_vencimento=contract.due_date,
        taxa_reajuste=contract.reajustment_rate,
        pdf_assinado=None,
        casa_id=contract.house_id,
        template_id=contract.template_id,
        inquilino_id=contract.tenant_id,
        user_id=current_user.user_id,
    )

    session.add(new_contract)
    await session.commit()
    await session.refresh(new_contract)

    return map_contract_to_response(new_contract, house, tenant)


@router.patch(
    "/contracts/{contract_id}",
    response_model=ContractResponse,
    description="Upload a signed contract by its id",
)
async def upload_contract(
    contract_id: int,
    signed_pdf: UploadFile = File(...),
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

    key = await session.execute(select(Props.column).limit(1))
    key_response = key.scalar_one_or_none()
    file_path = GCStorage(key_response).upload_file(signed_pdf, "pdf")

    contract.pdf_assinado = file_path
    await session.commit()
    await session.refresh(contract)

    house_result = await session.execute(
        select(Houses)
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Houses.id == contract.casa_id)
        .where(Properties.user_id == current_user.user_id)
    )
    house = house_result.scalar_one_or_none()

    tenant_result = await session.execute(
        select(Tenant)
        .where(Tenant.id == contract.inquilino_id)
        .where(Tenant.user_id == current_user.user_id)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not house:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.FORBIDDEN_HOUSE,
        )

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=api_messages.FORBIDDEN_TENANT,
        )

    return map_contract_to_response(contract, house, tenant)


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


@router.post(
    "/contracts/{contract_id}/pdf",
    description="Generate a contract pdf by its id",
    status_code=status.HTTP_200_OK,
    response_class=PDFResponse,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Return a PDF file",
        }
    },
)
async def generate_contract_pdf(
    contract_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> PDFResponse:
    result = await session.execute(
        select(Contract, Template, Tenant, Houses, Properties)
        .join(Template, Contract.template_id == Template.id)
        .join(Tenant, Contract.inquilino_id == Tenant.id)
        .join(Houses, Contract.casa_id == Houses.id)
        .join(Properties, Houses.propriedade_id == Properties.id)
        .where(Contract.id == contract_id, Contract.user_id == current_user.user_id)
        .where(Tenant.user_id == current_user.user_id)
        .where(Properties.user_id == current_user.user_id)
    )
    result_data = result.one_or_none()

    if not result_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.CONTRACT_NOT_FOUND,
        )

    contract: Contract
    template: Template
    tenant: Tenant
    house: Houses
    property: Properties
    guarantor: Guarantor | None

    contract, template, tenant, house, property = result_data

    inspection_data = await session.execute(
        select(Inspection).where(Inspection.contrato_id == contract_id)
    )
    inspection: Inspection | None = inspection_data.scalar_one_or_none()

    if template.garantia == "fiador":
        fiador = await session.execute(
            select(Guarantor).where(Guarantor.inquilino_id == tenant.id)
        )
        guarantor = fiador.scalar_one_or_none()
    else:
        guarantor = None

    try:
        html_template = f"""
        <html><head><title>Contrato de Aluguel&#160;</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
<body>
<div style="page-break-before:always; page-break-after:always"><div style="text-align: justify; text-justify: inter-word;"><h3 style="text-align: center;"><b>CONTRATO DE LOCA&#199;&#195;O DE IM&#211;VEL {str(template.tipo_contrato).upper()}<br/></b></h3>
<p><b>LOCADOR</b>: {current_user.nome.upper()} , {current_user.estado_civil.upper()} , {current_user.profissao.upper()} , portador do CPF n&#186; {current_user.cpf.upper()} , residente e domiciliado &#224; {current_user.rua.upper()} , {current_user.numero} ,{current_user.bairro.upper()} , {current_user.cep} , {current_user.cidade.upper()} , {current_user.estado.upper()} .</p>
<p><b>LOCAT&#193;RIO</b>: {tenant.nome.upper()} , {tenant.estado_civil.upper()} , {tenant.profissao.upper()} , portador do CPF n&#186; {tenant.cpf} , residente e domiciliado &#224; {tenant.rua.upper()} , {tenant.numero} , {tenant.bairro.upper()} , {tenant.cep} , {tenant.cidade.upper()} , {tenant.estado.upper()}. </p>
{"<p><b>FIADOR</b>: " + str(guarantor.nome.upper()) + " , " + str(guarantor.estado_civil.upper()) + " , " + str(guarantor.profissao.upper()) + ", portador do CPF n&#186; " + (guarantor.cpf) + ", residente e domiciliado &#224; " + (guarantor.rua.upper()) + " , " + str(guarantor.numero) + " , " + (guarantor.bairro.upper()) + " , " + (guarantor.cep) + " , " + str(guarantor.cidade.upper()) + " , " + str(guarantor.estado.upper()) + ".</p>" if template.garantia == "fiador" and guarantor is not None else ""}
<p><b>CL&#193;USULA PRIMEIRA - DO OBJETO DA LOCA&#199;&#195;O<br/></b></p>
<p><b>1.1 </b>O objeto deste contrato de loca&#231;&#227;o &#233; o im&#243;vel situado na {property.rua.upper()} , {property.numero} ,{property.bairro.upper()} , {property.cep} , {property.cidade.upper()} , {property.estado.upper()} , no exato estado do termo de vistoria e fotos em anexo.</p>
<p><b>{"1.2 </b> Comp&#245;e o objeto da loca&#231;&#227;o, uma vaga de garagem , localizada na propriedade.</p>" if template.garagem is True else " "} 
<p><b>CL&#193;USULA SEGUNDA - DA DESTINA&#199;&#195;O DO IM&#211;VEL<br/></b></p>
<p><b>{"2.1 </b> O LOCATÁRIO declara que o imóvel, ora locado, destina-se única e exclusivamente para o seu uso RESIDENCIAL." if template.tipo_contrato == "residencial" else "2.1 </b> O LOCATÁRIO declara que o imóvel, ora locado, destina-se única e exclusivamente para o seu uso COMERCIAL."}</p>
<p><b>2.2 </b> O LOCATÁRIO obriga por si e demais dependentes a cumprir e a fazer cumprir integralmente as disposições legais sobre o Condomínio, a sua Convenção e o seu Regulamento Interno."</p>
<p><b>CL&#193;USULA TERCEIRA - DO PRAZO DE VIG&#202;NCIA<br/></b></p>
<p><b>3.1 </b>O prazo da loca&#231;&#227;o &#233; de {(contract.data_fim.year - contract.data_inicio.year) * 12 + (contract.data_fim.month - contract.data_inicio.month)} meses, iniciando-se em {contract.data_inicio.strftime('%d/%m/%Y')} com t&#233;rmino em {contract.data_fim.strftime('%d/%m/%Y')} , independentemente de aviso, notifica&#231;&#227;o ou interpela&#231;&#227;o judicial ou extrajudicial.<br/></p>
<p><b>3.2</b> Findo o prazo ajustado, se o locat&#225;rio continuar na posse do im&#243;vel alugado por mais de trinta dias sem oposi&#231;&#227;o do locador, presumir - se - &#225; prorrogada a loca&#231;&#227;o por prazo indeterminado, mantidas as demais cl&#225;usulas e condi&#231;&#245;es do contrato.</p>
<p><b>CL&#193;USULA QUARTA - DA FORMA DE PAGAMENTO<br/></b></p>
<p><b>4.1 </b>O aluguel mensal dever&#225; ser pago at&#233; o dia {contract.dia_vencimento } ({num2words(contract.dia_vencimento, lang='pt-br')}) do m&#234;s subsequente ao vencido, no valor de R$ {contract.valor_base} {num2words(contract.valor_base, lang='pt-br')}{"." if contract.taxa_reajuste is None else ", reajustados anualmente, pelo &#237;ndice " + str(contract.taxa_reajuste) +" , reajustamento este sempre incidente e calculado sobre o &#250;ltimo aluguel pago no &#250;ltimo m&#234;s do ano anterior."}</p>
<p><b>CL&#193;USULA QUINTA - DA MULTA E JUROS DE MORA<br/></b></p>
<p><b>5.1</b> Em caso de mora no pagamento do aluguel, o valor ser&#225; corrigido pelo IGP-M at&#233; o dia do efetivo pagamento e acrescido da multa morat&#243;ria de 10% (dez por cento) e dos juros de 1% (um por cento) ao m&#234;s e ensejar&#225; a sua cobran&#231;a atrav&#233;s de advogado.</p>
<p><b>5.2</b> Ficam desde j&#225; fixados os honor&#225;rios advocat&#237;cios em 10% (dez por cento), se amig&#225;vel a cobran&#231;a e, de 20% (vinte por cento), se judicial.</p>
<p><b>5.3</b> Caso o LOCAT&#193;RIO n&#227;o regularize o pagamento no prazo de 15 dias, o LOCADOR ter&#225; o direito de rescindir o presente contrato, com o despejo por descumprimento contratual, nos termos da Lei do Inquilinato <b>(Art. 9, inc. III da Lei n&#186; 8.245/91)</b>, sem preju&#237;zo da cobran&#231;a dos alugu&#233;is e encargos vencidos, dos danos causados ao im&#243;vel e das despesas judiciais e extrajudiciais decorrentes do despejo.</p>
<p><b>CL&#193;USULA SEXTA - DA CONSERVA&#199;&#195;O, REFORMAS E BENFEITORIAS<br/>NECESS&#193;RIAS<br/></b></p>
<p><b>6.1</b> Ao LOCAT&#193;RIO recai a responsabilidade por zelar pela conserva&#231;&#227;o, limpeza e seguran&#231;a do im&#243;vel.</p>
<p><b>6.2</b> As benfeitorias necess&#225;rias introduzidas pelo LOCAT&#193;RIO, ainda que n&#227;o autorizadas pelo LOCADOR, bem como as &#250;teis, desde que autorizadas, ser&#227;o indeniz&#225;veis e permitem o exerc&#237;cio do direito de reten&#231;&#227;o. As benfeitorias voluptu&#225;rias n&#227;o ser&#227;o indeniz&#225;veis, podendo ser levantadas pelo LOCAT&#193;RIO, finda a loca&#231;&#227;o, desde que sua retirada n&#227;o afete a estrutura e a subst&#226;ncia do im&#243;vel.</p>
<p><b>6.3</b> O LOCAT&#193;RIO est&#225; obrigado a devolver o im&#243;vel em perfeitas condi&#231;&#245;es de limpeza, conserva&#231;&#227;o e pintura, quando finda ou rescindida esta aven&#231;a, conforme constante no termo de vistoria em anexo.</p>
<p><b>6.4</b> O LOCAT&#193;RIO n&#227;o poder&#225; realizar obras que alterem ou modifiquem a estrutura do im&#243;vel locado, sem pr&#233;via autoriza&#231;&#227;o por escrito da LOCADORA. No caso de pr&#233;via autoriza&#231;&#227;o, as obras ser&#227;o incorporadas ao im&#243;vel, sem que caiba ao LOCAT&#193;RIO qualquer indeniza&#231;&#227;o pelas obras ou reten&#231;&#227;o por benfeitorias.</p>
<p><b>6.5</b> Cabe ao LOCAT&#193;RIO verificar a voltagem e a capacidade de instala&#231;&#227;o el&#233;trica existente no im&#243;vel, sendo de sua exclusiva responsabilidade pelos danos e preju&#237;zos que venham a ser causados em seus equipamentos el&#233;trico-eletr&#244;nico por inadequa&#231;&#227;o &#224; voltagem e/ou capacidade instalada. Qualquer altera&#231;&#227;o da voltagem dever&#225; de imediato ser comunicada ao(a) LOCADOR(A), por escrito. Ao final da loca&#231;&#227;o, antes de fazer a entrega das chaves, o(a) LOCAT&#193;RIO(A) dever&#225; proceder a mudan&#231;a para a voltagem original.</p>
<p><b>6.6</b> O LOCADOR deve responder pelos v&#237;cios ou defeitos anteriores &#224; loca&#231;&#227;o.</p>
<p><b>PAR&#193;GRAFO &#218;NICO </b>: O LOCAT&#193;RIO declara receber o im&#243;vel em perfeito estado de conserva&#231;&#227;o e perfeito funcionamento devendo observar o que consta no termo de vistoria, n&#227;o respondendo por v&#237;cios ocultos ou anteriores &#224; loca&#231;&#227;o. </p>
<p><b>CL&#193;USULA S&#201;TIMA - DAS TAXAS E TRIBUTOS<br/></b></p>
<p><b>7.1</b> Todas as taxas e tributos incidentes sobre o im&#243;vel, tais como condom&#237;nio, IPTU, bem como despesas ordin&#225;rias de condom&#237;nio e quaisquer outras despesas que reca&#237;rem sobre o im&#243;vel, ser&#227;o de responsabilidade do LOCAT&#193;RIO, o qual arcar&#225; tamb&#233;m com as despesas provenientes de sua utiliza&#231;&#227;o tais como liga&#231;&#227;o e consumo de luz, for&#231;a, &#225;gua e g&#225;s queser&#227;o pagas diretamente &#224;s empresas concession&#225;rias dos referidos servi&#231;os, que ser&#227;odevidos a partir desta data independente da troca de titularidade.</p>
<p><b>CL&#193;USULA OITAVA - DOS SINISTROS<br/></b></p>
<p><b>8.1</b> No caso de sinistro do pr&#233;dio, parcial ou total, que impossibilite a habita&#231;&#227;o do im&#243;vel locado, o presente contrato estar&#225; rescindido, independentemente de aviso ou interpela&#231;&#227;o judicial ou extrajudicial.</p>
<p><b>8.2</b> No caso de inc&#234;ndio parcial, obrigando obras de reconstru&#231;&#227;o, o presente contrato ter&#225; suspensa a sua vig&#234;ncia, sendo devolvido ao LOCAT&#193;RIO ap&#243;s a reconstru&#231;&#227;o, que ficar&#225; prorrogado pelo mesmo tempo de dura&#231;&#227;o das obras de reconstru&#231;&#227;o. </p>
<p><b>CL&#193;USULA NONA - DA SUBLOCA&#199;&#195;O<br/></b></p>
<p><b>9.1</b> &#201; {"vedado" if template.sublocacao is False else "permitido"} ao LOCAT&#193;RIO sublocar, transferir ou ceder o im&#243;vel, sendo nulo de pleno direito qualquer ato praticado com este fim sem o consentimento pr&#233;vio e por escrito do LOCADOR. </p>
<p><b>CL&#193;USULA D&#201;CIMA - DA DESAPROPRIA&#199;&#195;O<br/></b></p>
<p><b>10.1</b> Em caso de desapropria&#231;&#227;o total ou parcial do im&#243;vel locado, ficar&#225; rescindido de pleno direito o presente contrato de loca&#231;&#227;o, sendo pass&#237;vel de indeniza&#231;&#227;o as perdas e danos efetivamente demonstradas. </p>
<p><b>CL&#193;USULA D&#201;CIMA PRIMEIRA - DOS CASOS DE FALECIMENTO<br/></b></p>
<p><b>11.1</b> Falecendo o LOCADOR, ficam os seus sucessores sub-rogados dos direitos do presente contrato, devendo o LOCAT&#193;RIO seguir depositando o valor do aluguel em conta indicada pelo inventariante, ap&#243;s devidamente notificado.</p>
<p><b>11.2</b> Falecendo o LOCAT&#193;RIO, ficam os seus sucessores sub-rogados dos direitos do presente contrato, devendo decidir dentro de 30 dias da continuidade ou n&#227;o da LOCA&#199;&#195;O. O locador deve ser notificado da morte do LOCAT&#193;RIO e informado de quem ser&#225; o novo sucessor. </p>
<p><b>CL&#193;USULA D&#201;CIMA SEGUNDA - DA GARANTIA<br/></b></p>
<p><b>{str(template.garantia).upper()}<br/></b></p>
<p><b>12.1</b> {"O FIADOR, e principal pagador do LOCATÁRIO, responde solidariamente por todos os pagamentos descritos neste contrato, até a efetiva entrega das chaves ao LOCADOR e termo de vistoria do imóvel." if template.garantia == "fiador" else "Como garantia de fiança o LOCATÁRIO depositará, na conta correspondente em nome do LOCADOR, no ato de assinatura do contrato uma caução no valor de R$ " + str(contract.valor_caucao) + " equivalente a " + str(contract.valor_caucao//contract.valor_base) + " meses de aluguel."} </p>
<p><b>12.2</b> {"Falecendo o FIADOR, deve o LOCATÁRIO, no prazo 30 (trinta) dias, indicar substituto idôneo, nas mesmas condições do atual FIADOR, que possa garantir o valor locativo e encargos do referido imóvel, ou prestar seguro fiança de empresa idônea." if template.garantia == "fiador" else "O valor da caução será devolvido ao LOCATÁRIO, após a entrega das chaves e termo de vistoria do imóvel, descontando-se os débitos eventualmente existentes."}</p>
<p><b>CL&#193;USULA D&#201;CIMA TERCEIRA - DAS VISTORIAS<br/></b></p>
<p><b>13.1 </b>&#201; facultado ao LOCADOR, mediante aviso pr&#233;vio, vistoriar o im&#243;vel, por si ou seus procuradores, sempre que achar conveniente, para a certeza do cumprimento das obriga&#231;&#245;es assumidas neste contrato. </p>
<p><b>CL&#193;USULA D&#201;CIMA QUARTA - DOS ANIMAIS DOM&#201;STICOS<br/></b></p>
<p><b>14.1</b> &#201; {"permitido" if template.animais is True else "proibido"} a presen&#231;a de animais dom&#233;sticos no interior do im&#243;vel.</p>
<p><b>CL&#193;USULA D&#201;CIMA QUINTA - DAS INFRA&#199;&#213;ES AO CONTRATO<br/></b></p>
<p><b>15.1</b> A n&#227;o observ&#226;ncia de qualquer das cl&#225;usulas do presente contrato, sujeita o infrator &#224; multa de 3 vezes o valor do aluguel, tomando-se por base, o &#250;ltimo aluguel vencido.</p>
<p><b>CL&#193;USULA D&#201;CIMA SEXTA - DA RESCIS&#195;O DO CONTRATO<br/></b></p>
<p><b>16.1</b> A rescis&#227;o previamente &#224; vig&#234;ncia do presente contrato, culmina em multa contratual <b>calculada da seguinte forma: </b> {3 * contract.valor_base} / {(contract.data_fim.year - contract.data_inicio.year) * 12 + (contract.data_fim.month - contract.data_inicio.month)} = R$ {(3 * contract.valor_base) / ((contract.data_fim.year - contract.data_inicio.year) * 12 + (contract.data_fim.month - contract.data_inicio.month)):.2f} ao m&#234;s X os meses faltantes para o t&#233;rmino do contrato. </p>
<p><b>16.2</b> Ap&#243;s o prazo de vig&#234;ncia do presente, podem as partes rescindirem o contrato mediante aviso pr&#233;vio de 30 dias. </p>
<p><b>CL&#193;USULA D&#201;CIMA S&#201;TIMA - DA OBSERV&#194;NCIA &#192; LGPD<br/></b></p>
<p><b>17.1</b> O LOCAT&#193;RIO declara expresso CONSENTIMENTO que o LOCADOR ir&#225; coletar, tratar e compartilhar os dados necess&#225;rios ao cumprimento do contrato, nos termos do <b>Art. 7&#186;, inc. V</b> da <b>LGPD</b>, os dados necess&#225;rios para cumprimento de obriga&#231;&#245;es legais, nos termos do <b>Art. 7&#186;, inc. II</b> da <b>LGPD</b>, bem como os dados, se necess&#225;rios, para prote&#231;&#227;o ao cr&#233;dito, conforme autorizado pelo <b>Art. 7&#186;, inc. V</b> da <b>LGPD</b>.</p>
<p><b>CL&#193;USULA D&#201;CIMA OITAVA - TERMOS GERAIS<br/></b></p>
<p><b>18.1</b> O LOCAT&#193;RIO se obriga a respeitar os direitos de vizinhan&#231;a com rigorosa observ&#226;ncia da Conven&#231;&#227;o, Regulamento Interno ou outros regulamentos porventura existentes, quando a unidade estiver inserida em condom&#237;nio, ficando respons&#225;vel pelas multas que vierem a ser aplicadas em raz&#227;o de infra&#231;&#245;es cometidas.</p>
<p><b>18.2</b> Somente ser&#225; permitido ao LOCAT&#193;RIO colocar placas, letreiros, cartazes ou quaisquer inscri&#231;&#245;es ou sinais, bem como aparelhos de ar condicionado, antenas, etc. nas partes externas do im&#243;vel locado, se for observado o previsto na legisla&#231;&#227;o municipal, e em caso de unidade integrante de condom&#237;nio observar, tamb&#233;m, o disposto na conven&#231;&#227;o e regimento interno, e pr&#233;via autoriza&#231;&#227;o do s&#237;ndico. </p>
<p><b>18.3</b> As partes contratantes obrigam-se por si, herdeiros e/ou sucessores.</p>
<p><b>CL&#193;USULA D&#201;CIMA NONA - DO FORO<br/></b></p>
<p><b>19.1</b> As partes elegem o foro de {current_user.cidade.upper()}/{current_user.estado.upper()} para dirimirem qualquer lit&#237;gio decorrente dopresente termo.</p>
<p>E, por assim estarem justos e contratados, mandaram extrair o presente instrumento em tr&#234;s (03) vias, para um s&#243; efeito, assinando-as, juntamente com as testemunhas, a tudo presentes. </p>
<p><br/><br/></p>
<div style="text-align: center;">
<p>LOCADOR. ________________________________________<br/><br/></p>
<p>LOCATÁRIO. ______________________________________<br/><br/></p>
<p>FIADOR. _________________________________________<br/><br/></p>
<p>TESTEMUNHA 1. __________________________________<br/><br/></p>
<p>TESTEMUNHA 2. __________________________________<br/><br/></p>
<p>DATA/LOCAL: ___/___/_____ - ____________________<br/></p>
</div>
{"<p>ANEXOS:<br/></p>" if inspection is not None else ""}
{"<p>1. Termo de vistoria do im&#243;vel</p>" if inspection is not None else ""}
</div></div>
</body></html>
        """

        pdf = HTML(string=html_template).write_pdf()

        return PDFResponse(content=pdf, filename=f"Contrato_Aluguel.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {e}")
