from typing import Callable, Dict, List, Optional
from enum import Enum
from functools import reduce
from datetime import datetime
from pydantic.networks import EmailStr
from sqlmodel import SQLModel, Field, Column, ForeignKey, VARCHAR, CHAR, INTEGER, BIGINT
from sqlalchemy.dialects.postgresql import JSONB


class UserCreate(SQLModel, table=True):
    """
    Модель для создания пользователя
    """

    id: Optional[int] = Field(default=None, sa_column=Column("id", INTEGER, primary_key=True, autoincrement=True, unique=True))

    user_id: int = Field(..., title="ID Пользователя", sa_column=Column("user_id", INTEGER, unique=True))
    phone: str = Field(..., title="Телефон пользователя", sa_column=Column("phone", VARCHAR, unique=True))

    class Config:
        shema_extra = {
            "example": {
                "user_id": 1,
                "phone": "77777777777"
            },
        }


class GetUsers(SQLModel):
    """
    Получение списка пользователей
    """
    users: Optional[List[UserCreate]] = Field(None, title="Список пользователей")
