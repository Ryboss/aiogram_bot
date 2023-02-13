import logging

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database.session import get_session
from app.models.companies import (
    Companies, ResponseCompanies
)
from app.models.utils import ExcelModel
from app.crud import companies
from app.core.utils import sql_validation_error, generate_json_to_excel


log = logging.getLogger()


router = APIRouter(prefix="/api/v1/companies", tags=["v1", "Companies"], default_response_class=ORJSONResponse)

PERMISSION_EXCEPTION = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@router.post(
    "/create_company",
    status_code=201,
    response_model=Companies,
)
async def create_company(
    user: Companies,
    session: AsyncSession = Depends(get_session)
) -> Companies:
    """
    Создание Компании
    """

    return await companies.create(session=session, item=user)


@router.post(
    "/get_companies",
    status_code=201
)
async def get_companies(
    file_path: str = Query(..., description="PATH для сохранения Excel"),
    session: AsyncSession = Depends(get_session),
) -> str:
    """
    Получение списка Компаний
    """

    data = await companies.get_companies(session=session)

    titles = ["Название компании", "Почта", "Номер телефона", "Адрес"]
    result = [ExcelModel(titles=titles, title="Список пользователей", data=data, file_path=file_path)]

    return await generate_json_to_excel(data=result, file_path=file_path)
