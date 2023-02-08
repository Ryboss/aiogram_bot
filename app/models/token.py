from typing import Optional, List
from datetime import datetime
from fastapi import Form
from sqlmodel import SQLModel, Field, Column, INTEGER
# from pydantic import EmailStr

_token_example = "_" * 36 + "." + "_" * 54 + "." + "_" * 42


class OAuth2RefreshRequestForm(SQLModel):
    """
    Форма запроса Refresh Token'а
    """

    grant_type: str = Form(None, regex="refresh_token", description="Должно равняться `refresh_token` для обновления токена")
    refresh_token: str = Form(..., example=_token_example)

    class Config:
        schema_extra = {
            "example": {
                "grant_type": "refresh_token",
                "refresh_token": _token_example,
            },
        }


class TokenPayload(SQLModel):
    """
    Структура токена
    """

    sub: str = Field(..., description="Почта")
    exp: Optional[datetime] = Field(default=None, description="Дата истекания токена")


class Token(SQLModel):
    """
    Форма ответа при авторизации
    Форма ответа при запросе на обновление Access Token'а через Refresh Token
    """

    access_token: str = Field(..., title="Access Token")
    refresh_token: Optional[str] = Field(default=None, title="Refresh Token")
    token_type: str = Field(...)
    expires_in: Optional[int] = Field(default=None, description="Время жизни токена в минутах")

    class Config:
        schema_extra = {
            "example": {
                "access_token": _token_example,
                "refresh_token": _token_example,
                "token_type": "Bearer",
                "expires_in": 43200,
            },
        }


class TokenData(SQLModel):
    """
    Валидация данных при создании токена
    """

    email: str = Field(..., title="Почта")
    scopes: List[str] = Field(default=[], description = "Набор прав пользователя, указанный через scopes")


class Tokens_Blacklist(SQLModel, table=True):
    """
    Хранение токенов разлогинившихся пользователей, но не истёкших по времени для предотвращения использования,
    а также старых токенов при получении новых через Refresh Token.
    """

    id: Optional[int] = Field(default=None, sa_column=Column("id", INTEGER, primary_key=True, autoincrement=True, unique=True))
    token: str = Field(..., description="Refresh Token пользоваетля")
    expiration: Optional[datetime] = Field(..., description = "Поле истекания срока токена после которого его дальнейшее хранение не требуется", nullable=True)


class UserLogoutResponse(SQLModel):
    """
    Форма ответа при запросе деавторизации
    """

    result: bool = Field(..., description="Результат выполнения запроса")


class UserResetPasswordRequest(SQLModel):
    """
    Форма запроса при сбросе пароля
    """

    email: str = Field(..., title="Почта")


class UserResetPasswordResponse(SQLModel):
    """
    Форма ответа при сбросе пароля
    """

    result: bool = Field(..., description="Результат выполнения запроса")


class UserResetPasswordEmail(SQLModel):
    """
    Поля для письма по форме сброса пароля
    """

    sv_name: str = Field(..., title="Имя директора компании", description="Иванов И.И.")
    sv_email: str = Field(..., title="Почта директора компании")

    user_name: str = Field(..., title="Имя пользователя сбросившего пароль", description="Иванов И.И.")
    user_login: str = Field(..., title="Логин пользователя")
    user_password: str = Field(..., title="Новый пароль пользователя")
