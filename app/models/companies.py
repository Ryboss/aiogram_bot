from sqlmodel import SQLModel, Field, Column, VARCHAR, INTEGER, BIGINT
from typing import List, Dict, Optional
from pydantic import EmailStr


class Companies(SQLModel, table=True):
    """
    Модель создания компании
    """

    id: Optional[int] = Field(default=None, sa_column=Column("id", INTEGER, primary_key=True, autoincrement=True, unique=True))

    company_name: str = Field(..., title="Название компании", sa_column=Column("company_name", VARCHAR, unique=True))
    adress: str = Field(..., title="Адрес компании", sa_column=Column("adress", VARCHAR, unique=True))
    company_phone: int = Field(..., title="Номер телефона компании", sa_column=Column("company_phone", BIGINT, unique=True))
    email: EmailStr = Field(..., title="Почта компании", sa_column=Column("email", VARCHAR, unique=True))

    class Config:
        shema_extra = {
            "example": {
                "company_name": "Имя компании",
                "email": "test@mail.ru",
                "adress": "Test adress",
                "company_phone": "77777777777"
            },
        }


class ResponseCompanies(SQLModel):
    """
    Получение компании
    """

    company_name: str = Field(..., title="Название компании")
    adress: str = Field(..., title="Адрес компании")
    company_phone: int = Field(..., title="Номер телефона компании")
    email: EmailStr = Field(..., title="Почта компании")
