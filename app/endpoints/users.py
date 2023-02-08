import logging

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database.session import get_session
from app.models.users import (
    Users, GetUsers, ResponsUser
)
from app.models.utils import ExcelModel
from app.crud import users
from app.core.utils import sql_validation_error, generate_json_to_excel


log = logging.getLogger()

router = APIRouter(prefix="/api/v1/users", tags=["v1", "Users"], default_response_class=ORJSONResponse)

PERMISSION_EXCEPTION = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


@router.post(
    "/create",
    status_code=201,
    response_model=Users,
)
async def create_user(
    user: Users,
    session: AsyncSession = Depends(get_session)
) -> Users:
    """
    Создание пользователя
    """

    return await users.create(session=session, item=user)


@router.post(
    "/get_users",
    status_code=201

)
async def get_users(
    file_path: str = Query(..., description="PATH для сохранения Excel"),
    session: AsyncSession = Depends(get_session),
) -> Optional[List[Users]]:
    """
    Создание пользователя
    """

    data = await users.get_users(session=session)

    titles = ["Имя пользователя", "ID Пользователя", "Телефон"]
    result = [ExcelModel(titles=titles, title="Список пользователей", data=data, file_path=file_path)]

    await generate_json_to_excel(data=result, file_path=file_path)

    return
