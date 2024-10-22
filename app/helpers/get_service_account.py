from sqlalchemy import select
from app.models.models import Props
from sqlalchemy.ext.asyncio import AsyncSession

async def get_service_account(session: AsyncSession) -> dict:
    result = await session.execute(select(Props.column).limit(1))
    key = result.scalar()
    if key is None:
        raise Exception("No service account key found")
    return key

    