from app.models.models import Houses, Properties, Owner, Tenant
from app.schemas.responses import HouseResponse, PropertyResponse, UserResponse, TenantResponse


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
