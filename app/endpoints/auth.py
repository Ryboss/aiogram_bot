# from typing import Optional
# from datetime import datetime
# from fastapi import APIRouter, Depends, Header
# from fastapi.security import OAuth2PasswordRequestForm
# from fastapi.responses import ORJSONResponse
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_session
# from app.core.config import JWT_EXPIRE_MINUTES
# from app.core.security import (
#     verify_password, create_access_token, create_refresh_token, CREDENTIALS_EXCEPTION, CREDENTIALS_USERNAME_EXCEPTION, CREDENTIALS_ROLE_EXCEPTION,
# )
# from app.crud.auth import add_blacklist_token, decode_access_token, get_current_user_token, validate_email, reset_user_password
# from app.models.token import Token, UserLogoutResponse, UserResetPasswordRequest, UserResetPasswordResponse, OAuth2RefreshRequestForm
# from app.crud import users, notifications

# router = APIRouter(prefix="/api/v1/auth", tags=["v1", "Auth"], default_response_class=ORJSONResponse)


# @router.post("/login", response_model=Token)
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     session: AsyncSession = Depends(get_session),
#     package_name: Optional[str] = Header(None),
# ) -> Token:
#     """
#     Авторизация пользователя
#     """

#     user, roles = await users.get_by_login_with_roles(session, form_data.username.lower())

#     if user is None or not verify_password(form_data.password, user.hashed_password):
#         raise CREDENTIALS_USERNAME_EXCEPTION
#     if (package_name is not None and "diagnostician_or_mobile_team" not in [role.alias for role in roles]):
#         raise CREDENTIALS_ROLE_EXCEPTION

#     return Token(
#         access_token=create_access_token(user.email),
#         refresh_token=create_refresh_token(user.email),
#         token_type="Bearer",
#         expires_in=JWT_EXPIRE_MINUTES,
#     )


# @router.post("/refresh", response_model=Token, response_model_exclude_none=True)
# async def refresh(
#     form_data: OAuth2RefreshRequestForm,
#     session: AsyncSession = Depends(get_session),
# ) -> Token:
#     """
#     Обновление токена с помощью Refresh Token'а
#     """

#     try:
#         payload = decode_access_token(form_data.refresh_token)

#         # Check if token is not expired
#         if payload and (exp := payload.get("exp")) is not None and datetime.utcfromtimestamp(float(exp)) > datetime.utcnow():
#             email: Optional[str] = payload.get("sub")  # type: ignore

#             # Validate email
#             if email is not None and await validate_email(session, email):
#                 # Create and return token
#                 token = Token(
#                     access_token=create_access_token(email),
#                     refresh_token=create_refresh_token(email),
#                     token_type="Bearer",
#                     expires_in=JWT_EXPIRE_MINUTES,
#                 )

#                 # user = await users.get_by_email(session, email)

#                 # if user and user.id:
#                 await notifications.update_token(session, old_token=form_data.refresh_token, token=token, email=email)

#                 return token
#     except Exception:
#         raise CREDENTIALS_EXCEPTION
#     raise CREDENTIALS_EXCEPTION


# @router.get("/logout", response_model=UserLogoutResponse)
# async def logout(
#     token: str = Depends(get_current_user_token),
#     session: AsyncSession = Depends(get_session),
# ) -> UserLogoutResponse:
#     """
#     Деавторизация пользователя
#     """

#     if await add_blacklist_token(session, token):
#         return UserLogoutResponse(result=True)
#     raise CREDENTIALS_EXCEPTION


# @router.post("/reset", response_model=UserResetPasswordResponse)
# async def reset_password(
#     form: UserResetPasswordRequest,
#     session: AsyncSession = Depends(get_session),
# ) -> UserResetPasswordResponse:
#     """
#     Сброс пароля пользователя
#     """

#     user = await users.get_by_email(session, form.email)
#     if user is None:
#         raise CREDENTIALS_USERNAME_EXCEPTION

#     return UserResetPasswordResponse(result=await reset_user_password(session, form.email))


# # @router.get("/reset/verify", response_model=UserResetPasswordResponse)
# # async def verify_token_before_reset_password(
# #     token: str = Depends(get_current_user_token),
# #     session: AsyncSession = Depends(get_session),
# # ) -> UserResetPasswordResponse:
# #     """
# #     Проверка токена на валидность (включая ограничения по времени жизни)
# #     """
# #
# #     return UserResetPasswordResponse(result=False)


# # @router.post("/reset/new", response_model=UserResetPasswordResponse)
# # async def set_new_password(
# #     form: UserResetPasswordRequest,
# #     token: str = Depends(get_current_user_token),
# #     session: AsyncSession = Depends(get_session),
# # ) -> UserResetPasswordResponse:
# #     """
# #     Сброс пароля пользователя
# #     """
# #
# #     return UserResetPasswordResponse(result=await reset_user_password(session, form.email))
