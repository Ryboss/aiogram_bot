from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError, PendingRollbackError
from typing import Optional, List

from app.models.users import UserCreate, GetUsers
from app.database.sql import GET_USERS

session = AsyncSession()


async def create(item: UserCreate, session: AsyncSession) -> UserCreate:
    """
    Создание пользователя
    """

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_users(session: AsyncSession) -> Optional[List[UserCreate]]:
    """
    Получение пользователей
    """
    print("22222222222222")
    users = await session.execute(GET_USERS())
    result = users.all()
    print(result)
    list_users: List[UserCreate] = []
    for user in result:
        list_users.append(UserCreate(**dict(user)))
    print(list_users)
    return list_users




