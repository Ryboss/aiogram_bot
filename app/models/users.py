from typing import Callable, Dict, List, Optional

from sqlmodel import SQLModel, Field, Column, VARCHAR, INTEGER


class Users(SQLModel, table=True):
    """
    Модель для создания пользователя
    """

    id: Optional[int] = Field(default=None, sa_column=Column("id", INTEGER, primary_key=True, autoincrement=True, unique=True))

    username: str = Field(..., title="Имя пользователя", sa_column=Column("username", VARCHAR, unique=True))
    user_id: int = Field(..., title="ID Пользователя", sa_column=Column("user_id", INTEGER, unique=True))
    phone: str = Field(..., title="Телефон пользователя", sa_column=Column("phone", VARCHAR, unique=True))

    class Config:
        shema_extra = {
            "example": {
                "user_id": 1,
                "phone": "77777777777"
            },
        }

class ResponsUser(SQLModel):
    """
    Ответ с данными пользователя без ID
    """

    username: str = Field(..., title="Имя пользователя")
    user_id: str = Field(..., title="ID Пользователя")
    phone: str = Field(..., title="Телефон пользователя")


class GetUsers(SQLModel):
    """
    Получение списка пользователей
    """
    users: Optional[List[Users]] = Field(None, title="Список пользователей")
