import logging

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database.session import get_session
from app.models.users import (
    UserCreate, GetUsers
)
from app.crud import users
from app.core.utils import sql_validation_error


log = logging.getLogger()

router = APIRouter(prefix="/api/v1/users", tags=["v1", "Users"], default_response_class=ORJSONResponse)

PERMISSION_EXCEPTION = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


@router.post(
    "/create",
    status_code=201,
    response_model=UserCreate,
)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> UserCreate:
    """
    Создание пользователя
    """
    print(user)
    print("3333333333")
    return await users.create(session=session, item=user)


@router.get(
    "/get_users",
    status_code=201

)
async def get_users(
    session: AsyncSession = Depends(get_session),
) -> Optional[List[UserCreate]]:
    """
    Создание пользователя
    """

    return await users.get_users(session=session)
