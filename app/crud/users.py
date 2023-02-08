from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError, PendingRollbackError
from typing import Optional, List

from app.models.users import Users, GetUsers, ResponsUser
from app.database.sql import GET_USERS

session = AsyncSession()


async def create(item: Users, session: AsyncSession) -> Users:
    """
    Создание пользователя
    """

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_users(session: AsyncSession) -> List[ResponsUser]:
    """
    Получение пользователей
    """

    users = await session.execute(GET_USERS())
    result = users.all()

    list_users: List[ResponsUser] = []
    for user in result:
        list_users.append(ResponsUser(**dict(user)))

    return list_users




