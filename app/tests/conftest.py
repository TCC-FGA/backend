import asyncio
from datetime import date
import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
import sqlalchemy
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.core import database_session
from app.core.config import get_settings
from app.core.security.jwt import create_jwt_token
from app.core.security.password import get_password_hash
from app.main import app as fastapi_app
from app.models.models import Base, Properties, Houses, Tenant, Template, Owner as User

default_user_id = "b75365d9-7bf9-4f54-add5-aeab333a087b"
default_user_email = "geralt@wiedzmin.pl"
default_user_password = "geralt"
default_user_telephone = "48123456789"
default_user_name = "Geralt of Rivia"
default_user_monthly_income = 5000.0
default_user_cpf = "12345678901"
default_user_birth_date = date(1990, 1, 1)
default_user_pix_key = "1234567890"
default_user_is_admin = False
default_user_birth_date_string = "1990-01-01"
default_user_access_token = create_jwt_token(default_user_id).access_token


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def fixture_setup_new_test_database() -> None:
    worker_name = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    test_db_name = f"test_db_{worker_name}"

    # create new test db using connection to current database
    conn = await database_session._ASYNC_ENGINE.connect()
    await conn.execution_options(isolation_level="AUTOCOMMIT")
    await conn.execute(sqlalchemy.text(f"DROP DATABASE IF EXISTS {test_db_name}"))
    await conn.execute(sqlalchemy.text(f"CREATE DATABASE {test_db_name}"))
    await conn.close()

    session_mpatch = pytest.MonkeyPatch()
    session_mpatch.setenv("DATABASE__DB", test_db_name)
    session_mpatch.setenv("SECURITY__PASSWORD_BCRYPT_ROUNDS", "4")

    # force settings to use now monkeypatched environments
    get_settings.cache_clear()

    # monkeypatch test database engine
    engine = database_session.new_async_engine(get_settings().sqlalchemy_database_uri)

    session_mpatch.setattr(
        database_session,
        "_ASYNC_ENGINE",
        engine,
    )
    session_mpatch.setattr(
        database_session,
        "_ASYNC_SESSIONMAKER",
        async_sessionmaker(engine, expire_on_commit=False),
    )

    # create app tables in test database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def fixture_clean_get_settings_between_tests() -> AsyncGenerator[None, None]:
    yield

    get_settings.cache_clear()


@pytest_asyncio.fixture(name="default_hashed_password", scope="session")
async def fixture_default_hashed_password() -> str:
    return get_password_hash(default_user_password)


@pytest_asyncio.fixture(name="session", scope="function")
async def fixture_session_with_rollback(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncSession, None]:
    # we want to monkeypatch get_async_session with one bound to session
    # that we will always rollback on function scope

    connection = await database_session._ASYNC_ENGINE.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    monkeypatch.setattr(
        database_session,
        "get_async_session",
        lambda: session,
    )

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture(name="client", scope="function")
async def fixture_client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=fastapi_app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as aclient:
        aclient.headers.update({"Host": "localhost"})
        yield aclient


@pytest_asyncio.fixture(name="default_user", scope="function")
async def fixture_default_user(
    session: AsyncSession, default_hashed_password: str
) -> User:
    default_user = User(
        user_id=default_user_id,
        email=default_user_email,
        senha_hash=default_hashed_password,
        nome=default_user_name,
        telefone=default_user_telephone,
        assinatura_hash="hashed_signature",
        cpf=default_user_cpf,
        data_nascimento=default_user_birth_date,
        profissao="Engineer",
        estado_civil="solteiro",
        rua="Rua Teste",
        bairro="Bairro Teste",
        numero=1,
        cep="11111-111",
        cidade="Cidade Teste",
        estado="DF",        
    )
    session.add(default_user)
    await session.commit()
    await session.refresh(default_user)
    return default_user


@pytest_asyncio.fixture(name="default_user_headers", scope="function")
def fixture_default_user_headers(default_user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {default_user_access_token}"}


@pytest_asyncio.fixture(name="default_property", scope="function")
async def fixture_default_property(
    session: AsyncSession, default_user: User
) -> Properties:
    property = Properties(
        apelido="Casa Teste",
        iptu=100.0,
        foto=None,
        rua="Rua Teste",
        bairro="Bairro Teste",
        numero=1,
        cep="11111-111",
        cidade="Cidade Teste",
        estado="DF",
        user_id=default_user.user_id,
    )

    session.add(property)
    await session.commit()
    await session.refresh(property)

    return property


@pytest_asyncio.fixture(name="default_house", scope="function")
async def fixture_default_house(
    session: AsyncSession, default_property: Properties
) -> Houses:
    house = Houses(
        apelido="Casa Teste",
        foto=None,
        qtd_comodos=3,
        banheiros=2,
        mobiliada=False,
        status="vaga",
        propriedade_id=default_property.id,
    )

    session.add(house)
    await session.commit()
    await session.refresh(house)

    return house


@pytest_asyncio.fixture(name="default_tenant", scope="function")
async def fixture_default_tenant(
    session: AsyncSession, default_property: Properties, default_user: User
) -> Tenant:
    tenant = Tenant(
        cpf="12345678900",
        contato="555-5555",
        email="teste@mail.com",
        nome="John Doe",
        profissao="Engineer",
        estado_civil="solteiro",
        data_nascimento=date(1990, 1, 1),
        contato_emergencia="61-99555-5556",
        renda=5000.0,
        num_residentes=2,
        user_id=default_user.user_id,
        rua="Rua Teste",
        bairro="Bairro Teste",
        numero=1,
        cep="11111-111",
        cidade="Cidade Teste",
        estado="DF",
    )

    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)

    return tenant


@pytest_asyncio.fixture(name="default_template", scope="function")
async def fixture_default_template(
    session: AsyncSession, default_user: User
) -> Template:
    template = Template(
        nome_template="Template Teste",
        descricao="Descrição Teste",
        garagem=True,
        garantia="caução",
        animais=False,
        sublocacao=False,
        tipo_contrato="residencial",
        user_id=default_user.user_id,
    )

    session.add(template)
    await session.commit()
    await session.refresh(template)

    return template
