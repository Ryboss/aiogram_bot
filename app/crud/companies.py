from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError, PendingRollbackError
from typing import Optional, List

from app.models.companies import Companies, ResponseCompanies
from app.database.sql import GET_USERS, GET_COMPANIES

session = AsyncSession()


async def create(item: Companies, session: AsyncSession) -> Companies:
    """
    Создание Компании
    """

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_companies(session: AsyncSession) -> List[ResponseCompanies]:
    """
    Получение списка компаний
    """

    companies = await session.execute(GET_COMPANIES())
    result = companies.all()

    list_users: List[ResponseCompanies] = []
    for user in result:
        list_users.append(ResponseCompanies(**dict(user)))

    return list_users




