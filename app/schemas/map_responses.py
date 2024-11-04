from app.models.models import (
    Houses,
    Properties,
    Owner,
    Tenant,
    Template,
    Contract,
    Expenses,
    Guarantor,
    PaymentInstallment,
)
from app.schemas.responses import (
    HouseResponse,
    PropertyResponse,
    UserResponse,
    TenantResponse,
    TemplateResponse,
    ContractResponse,
    ExpenseResponse,
    GuarantorResponse,
    PaymentInstallmentResponse,
)


def map_property_to_response(property: Properties) -> PropertyResponse:
    return PropertyResponse(
        id=property.id,
        nickname=property.apelido,
        photo=property.foto,
        iptu=property.iptu,
        owner_id=property.user_id,
        street=property.rua,
        neighborhood=property.bairro,
        number=property.numero,
        zip_code=property.cep,
        city=property.cidade,
        state=property.estado,
    )


def map_user_to_response(user: Owner) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        telephone=user.telefone,
        hashed_signature=user.assinatura_hash,
        cpf=user.cpf,
        birth_date=user.data_nascimento,
        name=user.nome,
        photo=user.foto,
    )


def map_house_to_response(house: Houses) -> HouseResponse:
    return HouseResponse(
        id=house.id,
        property_id=house.propriedade_id,
        photo=house.foto,
        nickname=house.apelido,
        room_count=house.qtd_comodos,
        bathrooms=house.banheiros,
        furnished=house.mobiliada,
        status=str(house.status),
    )


def map_tenant_to_response(tenant: Tenant) -> TenantResponse:
    return TenantResponse(
        id=tenant.id,
        cpf=tenant.cpf,
        contact=tenant.contato,
        email=tenant.email,
        name=tenant.nome,
        profession=tenant.profissao,
        marital_status=tenant.estado_civil,
        birth_date=tenant.data_nascimento,
        emergency_contact=tenant.contato_emergencia,
        income=tenant.renda,
        residents=tenant.num_residentes,
        street=tenant.rua,
        neighborhood=tenant.bairro,
        number=tenant.numero,
        zip_code=tenant.cep,
        city=tenant.cidade,
        state=tenant.estado,
    )


def map_template_to_response(template: Template) -> TemplateResponse:
    return TemplateResponse(
        id=template.id,
        template_name=template.nome_template,
        description=template.descricao,
        garage=template.garagem,
        warranty=str(template.garantia),
        animals=template.animais,
        sublease=template.sublocacao,
        contract_type=str(template.tipo_contrato),
    )


def map_contract_to_response(
    contract: Contract, house: Houses, tenant: Tenant
) -> ContractResponse:
    return ContractResponse(
        id=contract.id,
        deposit_value=contract.valor_caucao,
        start_date=contract.data_inicio,
        end_date=contract.data_fim,
        base_value=contract.valor_base,
        due_date=contract.dia_vencimento,
        reajustment_rate=str(contract.taxa_reajuste),
        signed_pdf=contract.pdf_assinado,
        house_id=contract.casa_id,
        template_id=contract.template_id,
        tenant_id=contract.inquilino_id,
        user_id=contract.user_id,
        house=HouseResponse(
            id=house.id,
            property_id=house.propriedade_id,
            photo=house.foto,
            nickname=house.apelido,
            room_count=house.qtd_comodos,
            bathrooms=house.banheiros,
            furnished=house.mobiliada,
            status=str(house.status),
        ),
        tenant=TenantResponse(
            id=tenant.id,
            cpf=tenant.cpf,
            contact=tenant.contato,
            email=tenant.email,
            name=tenant.nome,
            profession=tenant.profissao,
            marital_status=tenant.estado_civil,
            birth_date=tenant.data_nascimento,
            emergency_contact=tenant.contato_emergencia,
            income=tenant.renda,
            residents=tenant.num_residentes,
            street=tenant.rua,
            neighborhood=tenant.bairro,
            number=tenant.numero,
            zip_code=tenant.cep,
            city=tenant.cidade,
            state=tenant.estado,
        ),
    )


def map_expense_to_response(expense: Expenses) -> ExpenseResponse:
    return ExpenseResponse(
        id=expense.id,
        expense_type=str(expense.tipo_despesa),
        value=expense.valor,
        expense_date=expense.data_despesa,
        house_id=expense.casa_id,
    )


def map_guarantor_to_response(guarantor: Guarantor) -> GuarantorResponse:
    return GuarantorResponse(
        id=guarantor.id,
        tenant_id=guarantor.inquilino_id,
        cpf=guarantor.cpf,
        contact=guarantor.contato,
        email=guarantor.email,
        name=guarantor.nome,
        profession=guarantor.profissao,
        marital_status=guarantor.estado_civil,
        birth_date=guarantor.data_nascimento,
        comment=guarantor.comentario,
        income=guarantor.renda,
        street=guarantor.rua,
        neighborhood=guarantor.bairro,
        number=guarantor.numero,
        zip_code=guarantor.cep,
        city=guarantor.cidade,
        state=guarantor.estado,
    )


def map_payment_installment_to_response(
    payment_installment: PaymentInstallment,
) -> PaymentInstallmentResponse:
    return PaymentInstallmentResponse(
        id=payment_installment.id,
        installment_value=payment_installment.valor_parcela,
        fg_paid=payment_installment.fg_pago,
        payment_type=str(payment_installment.tipo_pagamento),
        due_date=payment_installment.data_vencimento,
        payment_date=payment_installment.data_pagamento,
        contract_id=payment_installment.contrato_id,
    )
