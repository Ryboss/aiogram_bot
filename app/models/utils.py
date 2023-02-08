from typing import Dict, List, Optional, Tuple, Union, TypeVar, Literal
from datetime import datetime as _datetime
from sqlmodel import SQLModel, Field


class GenericValidationError(SQLModel):
    """
    Модель detail для заполнения ошибок по форме ошибок валидации pydantic'а
    """

    loc: List[str] = Field(..., title="Поле с ошибкой", description="""Пример: ["company_id"]""", min_items=1)
    msg: Optional[str] = Field(default="", title="Сообщение с ошибкой", description="Не обязательно, не используется парсером")
    type: str = Field(..., title="Тип ошибки", description="Для SQL это к примеру: ForeignKeyViolationError, UniqueViolationError")


class ExcelModel(SQLModel):
    """
    Модель для генерации Excel
    """

    title: str = Field(default="Excel", title="Заголовок Excel файла")
    titles: List[Optional[str]] = Field(..., title="Названия колонок")
    data: list = Field(..., title="Данные для генерации")
