from typing import Optional
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserUpdateRequest(BaseModel):
    telephone: Optional[str] = None
    name: Optional[str] = None
    hashed_signature: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str


class UserCreateRequest(BaseRequest):
    email: EmailStr
    photo: Optional[str] = None
    password: str
    name: str
    telephone: str
    hashed_signature: Optional[str] = None
    cpf: str
    birth_date: date


class PropertyCreateRequest(BaseModel):

    nickname: str = Form(...)
    photo: UploadFile | None = File(None)
    iptu: float = Form(...)
    street: Optional[str] = Form(None)
    neighborhood: Optional[str] = Form(None)
    number: Optional[int] = Form(None)
    zip_code: str = Form(...)
    city: Optional[str] = Form(None)
    state: Optional[str] = Form(None)

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(...),
        iptu: float = Form(...),
        photo: UploadFile | None = File(None),
        street: Optional[str] = Form(None),
        neighborhood: Optional[str] = Form(None),
        number: Optional[str] = Form(None),
        zip_code: str = Form(...),
        city: Optional[str] = Form(None),
        state: Optional[str] = Form(None),
    ):
        return cls(
            nickname=nickname,
            iptu=iptu,
            photo=photo,
            street=street,
            neighborhood=neighborhood,
            number=int(number) if number is not None else None,
            zip_code=zip_code,
            city=city,
            state=state,
        )


class PropertyUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    photo: UploadFile | None = File(None)
    iptu: Optional[float] = None

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(None),
        photo: UploadFile | None = File(None),
        iptu: float = Form(None),
        street: str = Form(None),
        neighborhood: str = Form(None),
        number: str = Form(None),
        zip_code: str = Form(None),
        city: str = Form(None),
        state: str = Form(None),
    ):
        return cls(
            nickname=nickname,
            photo=photo,
            iptu=iptu,
            street=street,
            neighborhood=neighborhood,
            number=int(number) if number is not None else None,
            zip_code=zip_code,
            city=city,
            state=state,
        )


class HouseStatus(str, Enum):
    alugada = "alugada"
    vaga = "vaga"
    reforma = "reforma"


class HouseCreateRequest(BaseModel):
    nickname: str = Form(...)
    room_count: int = Form(...)
    photo: UploadFile | None = File(None)
    bathrooms: int = Form(...)
    furnished: bool = Form(False)
    status: HouseStatus = Form(...)

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(...),
        room_count: int = Form(...),
        photo: UploadFile | None = File(None),
        bathrooms: int = Form(...),
        furnished: bool = Form(False),
        status: HouseStatus = Form(...),
    ):
        return cls(
            nickname=nickname,
            room_count=room_count,
            photo=photo,
            bathrooms=bathrooms,
            furnished=furnished,
            status=status,
        )


class HouseUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    photo: UploadFile | None = File(None)
    room_count: Optional[int] = None
    bathrooms: Optional[int] = None
    furnished: Optional[bool] = None
    status: Optional[HouseStatus]

    @classmethod
    def as_form(
        cls,
        nickname: str = Form(None),
        room_count: int = Form(None),
        photo: UploadFile | None = File(None),
        bathrooms: int = Form(None),
        furnished: bool = Form(False),
        status: HouseStatus = Form(None),
    ):
        return cls(
            nickname=nickname,
            room_count=room_count,
            photo=photo,
            bathrooms=bathrooms,
            furnished=furnished,
            status=status,
        )


class TenantCreateRequest(BaseModel):
    cpf: str
    contact: str
    email: Optional[str] = None
    name: str
    profession: Optional[str] = None
    marital_status: Optional[str] = None
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    income: Optional[float] = None
    residents: Optional[int] = None

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: str
    city: Optional[str] = None
    state: Optional[str] = None


class TenantUpdateRequest(BaseModel):
    cpf: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    profession: Optional[str] = None
    marital_status: Optional[str] = None
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    income: Optional[float] = None
    residents: Optional[int] = None

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class ContractType(str, Enum):
    residencial = "residencial"
    comercial = "comercial"


class Warranty(str, Enum):
    fiador = "fiador"
    caução = "caução"
    nenhum = "nenhum"


class TemplateCreateRequest(BaseModel):
    template_name: str
    description: Optional[str] = None
    garage: bool
    warranty: Warranty
    animals: bool
    sublease: bool
    contract_type: ContractType


class TemplateUpdateRequest(BaseModel):
    template_name: Optional[str] = None
    description: Optional[str] = None
    garage: Optional[bool] = None
    warranty: Optional[Warranty] = None
    animals: Optional[bool] = None
    sublease: Optional[bool] = None
    contract_type: Optional[ContractType] = None


class ReajustmentRate(str, Enum):
    igpm = "IGPM"


class ContractCreateRequest(BaseModel):
    deposit_value: Optional[float] = None
    start_date: date
    end_date: date
    base_value: float
    due_date: int
    reajustment_rate: Optional[ReajustmentRate] = None
    house_id: int
    template_id: int
    tenant_id: int

    @classmethod
    def as_form(
        cls,
        deposit_value: float = Form(None),
        start_date: date = Form(...),
        end_date: date = Form(...),
        base_value: float = Form(...),
        due_date: int = Form(...),
        reajustment_rate: ReajustmentRate = Form(None),
        house_id: int = Form(...),
        template_id: int = Form(...),
        tenant_id: int = Form(...),
    ):
        return cls(
            deposit_value=deposit_value,
            start_date=start_date,
            end_date=end_date,
            base_value=base_value,
            due_date=due_date,
            reajustment_rate=reajustment_rate,
            house_id=house_id,
            template_id=template_id,
            tenant_id=tenant_id,
        )


class ExpenseType(str, Enum):
    manutenção = "manutenção"
    reparo = "reparo"
    imposto = "imposto"


class ExpenseCreateRequest(BaseModel):
    expense_type: ExpenseType
    value: float
    expense_date: date


class ExpenseUpdateRequest(BaseModel):
    expense_type: Optional[ExpenseType] = None
    value: Optional[float] = None
    expense_date: Optional[date] = None


class GuarantorCreateRequest(BaseModel):
    cpf: str
    contact: str
    email: Optional[str] = None
    name: str
    profession: Optional[str] = None
    marital_status: Optional[str] = None
    birth_date: Optional[date] = None
    comment: Optional[str] = None
    income: Optional[float] = None

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: str
    city: Optional[str] = None
    state: Optional[str] = None


class GuarantorUpdateRequest(BaseModel):
    contact: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    profession: Optional[str] = None
    marital_status: Optional[str] = None
    birth_date: Optional[date] = None
    comment: Optional[str] = None
    income: Optional[float] = None

    street: Optional[str] = None
    neighborhood: Optional[str] = None
    number: Optional[int] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class PaymentType(str, Enum):
    dinheiro = "dinheiro"
    cartão = "cartão"
    transferência = "transferência"
    outro = "outro"


class PaymentInstallmentCreateRequest(BaseModel):
    contract_id: int


class PaymentInstallmentUpdateRequest(BaseModel):
    fg_paid: bool
    payment_type: PaymentType
    payment_date: date


# Inspection
class EstadoPintura(str, Enum):
    nova = "Nova"
    bom_estado = "Em bom estado"
    com_defeitos = "Com alguns defeitos"


class TipoTinta(str, Enum):
    acrilica = "acrílica"
    latex = "latex"


class CondicaoEletrica(str, Enum):
    funcionando = "Funcionando"
    problemas = "Com problemas"
    desligada = "Desligada"


class Pintura(BaseModel):
    estado_pintura: EstadoPintura
    tipo_tinta: TipoTinta
    cor: Optional[str] = None


class Acabamento(BaseModel):
    condicao: Optional[str] = None
    observacoes: Optional[str] = None


class Eletrica(BaseModel):
    condicao: CondicaoEletrica
    observacoes: Optional[str] = None


class TrincosFechaduras(BaseModel):
    condicao: Optional[str] = None
    observacoes: Optional[str] = None


class PisoAzulejos(BaseModel):
    condicao: Optional[str] = None
    observacoes: Optional[str] = None


class VidracariaJanelas(BaseModel):
    condicao: Optional[str] = None
    observacoes: Optional[str] = None


class Telhado(BaseModel):
    condicao: Optional[str] = None
    observacoes: Optional[str] = None


class Hidraulica(BaseModel):
    condicao: Optional[str] = None
    observacoes: Optional[str] = None


class Mobilia(BaseModel):
    observacoes: Optional[str] = None


class Chaves(BaseModel):
    numero: Optional[int] = None
    observacoes: Optional[str] = None


class InspectionCreateRequest(BaseModel):
    data_vistoria: date
    pintura: Optional[Pintura] = None
    acabamento: Optional[Acabamento] = None
    eletrica: Optional[Eletrica] = None
    trincos_fechaduras: Optional[TrincosFechaduras] = None
    piso_azulejos: Optional[PisoAzulejos] = None
    vidracaria_janelas: Optional[VidracariaJanelas] = None
    telhado: Optional[Telhado] = None
    hidraulica: Optional[Hidraulica] = None
    mobilia: Optional[Mobilia] = None
    chave: Optional[Chaves] = None

    @classmethod
    def as_form(
        cls,
        data_vistoria: date = Form(...),
        estado_pintura: EstadoPintura = Form(...),
        tipo_tinta: TipoTinta = Form(...),
        cor: Optional[str] = Form(None),
        condicao_acabamento: Optional[str] = Form(None),
        observacoes_acabamento: Optional[str] = Form(None),
        condicao_eletrica: CondicaoEletrica = Form(...),
        observacoes_eletrica: Optional[str] = Form(None),
        condicao_trincos_fechaduras: Optional[str] = Form(None),
        observacoes_trincos_fechaduras: Optional[str] = Form(None),
        condicao_piso_azulejos: Optional[str] = Form(None),
        observacoes_piso_azulejos: Optional[str] = Form(None),
        condicao_vidracaria_janelas: Optional[str] = Form(None),
        observacoes_vidracaria_janelas: Optional[str] = Form(None),
        condicao_telhado: Optional[str] = Form(None),
        observacoes_telhado: Optional[str] = Form(None),
        condicao_hidraulica: Optional[str] = Form(None),
        observacoes_hidraulica: Optional[str] = Form(None),
        observacoes_mobilia: Optional[str] = Form(None),
        numero_chaves: Optional[int] = Form(None),
        observacoes_chaves: Optional[str] = Form(None),
    ):
        return cls(
            data_vistoria=data_vistoria,
            pintura=Pintura(
                estado_pintura=estado_pintura,
                tipo_tinta=tipo_tinta,
                cor=cor,
            ),
            acabamento=Acabamento(
                condicao=condicao_acabamento,
                observacoes=observacoes_acabamento,
            ),
            eletrica=Eletrica(
                condicao=condicao_eletrica,
                observacoes=observacoes_eletrica,
            ),
            trincos_fechaduras=TrincosFechaduras(
                condicao=condicao_trincos_fechaduras,
                observacoes=observacoes_trincos_fechaduras,
            ),
            piso_azulejos=PisoAzulejos(
                condicao=condicao_piso_azulejos,
                observacoes=observacoes_piso_azulejos,
            ),
            vidracaria_janelas=VidracariaJanelas(
                condicao=condicao_vidracaria_janelas,
                observacoes=observacoes_vidracaria_janelas,
            ),
            telhado=Telhado(
                condicao=condicao_telhado,
                observacoes=observacoes_telhado,
            ),
            hidraulica=Hidraulica(
                condicao=condicao_hidraulica,
                observacoes=observacoes_hidraulica,
            ),
            mobilia=Mobilia(
                observacoes=observacoes_mobilia,
            ),
            chave=Chaves(
                numero=numero_chaves,
                observacoes=observacoes_chaves,
            ),
        )
