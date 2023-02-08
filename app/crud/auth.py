# import os
# import string
# import secrets
# import smtplib

# from typing import Optional, List
# from datetime import datetime
# from fastapi import Depends, HTTPException, status
# from fastapi.security import SecurityScopes
# from pydantic import ValidationError
# from sqlalchemy.future import select
# from sqlalchemy.orm import Session
# from sqlalchemy.ext.asyncio import AsyncSession
# # from sqlalchemy.sql import exists
# from jose import JWTError
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# from app.core.config import EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_LOGIN, EMAIL_PASSWORD
# from app.database.session import get_session
# from app.database.sql import UPDATE_USER, AUTH_RESET_PASSWORD
# from app.core.security import CREDENTIALS_EXCEPTION, oauth2_scheme, decode_access_token
# from app.models.users import User, UserFullResponse, UserUpdate
# from app.models.token import TokenData, Tokens_Blacklist, UserResetPasswordEmail
# from app.crud import users


# def check_token(session: Session, token: str = "") -> bool:
#     """
#     Проверка на наличие токена в таблице деавторизованных неистёкших токенов
#     """

#     return session.query(select(Tokens_Blacklist).filter(Tokens_Blacklist.token == token).exists()).scalar()


# def check_email(session: Session, email: str = "") -> bool:
#     """
#     Проверка на наличие почты в таблице пользователей
#     """

#     return session.query(select(User).filter(User.email == email).exists()).scalar()


# async def add_blacklist_token(session: AsyncSession, token: str, expiration: Optional[datetime] = None) -> bool:
#     """
#     Добавление Access Token'а в таблицу деавторизованных токенов
#     """

#     payload = decode_access_token(token)
#     _exp: Optional[float] = payload.get("exp") if payload else None  # type: ignore
#     exp = datetime.utcfromtimestamp(_exp) if _exp else expiration
#     token_obj = Tokens_Blacklist(token=token, expiration=exp)

#     session.add(token_obj)
#     await session.commit()
#     # await session.refresh(token_obj)

#     return True


# async def is_token_blacklisted(session: AsyncSession, token: str) -> bool:
#     """
#     Проверка токена в таблице деавторизованных токенов
#     """

#     return await session.run_sync(check_token, token=token)


# async def validate_email(session: AsyncSession, email: str) -> bool:
#     """
#     Проверка почты в таблице пользователей
#     """

#     return await session.run_sync(check_email, email=email)


# async def get_current_user(
#     security_scopes: SecurityScopes,
#     session: AsyncSession = Depends(get_session),
#     token: str = Depends(oauth2_scheme),
# ) -> User:
#     """
#     Получение текущего пользователя по токену
#     """

#     # Scopes
#     if security_scopes.scopes:
#         authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
#     else:
#         authenticate_value = "Bearer"
#     credentials_exception = HTTPException(
#         status_code = status.HTTP_401_UNAUTHORIZED,
#         detail = "Credentials are not valid",
#         headers = {"WWW-Authenticate": authenticate_value})

#     if await is_token_blacklisted(session, token):
#         raise credentials_exception

#     try:
#         payload = decode_access_token(token)

#         if payload is None:
#             raise credentials_exception

#         email: Optional[str] = payload.get("sub")  # type: ignore
#         if email is None:
#             raise credentials_exception

#         # Scopes
#         token_scopes: List[str] = payload.get("scopes", [])  # type: ignore

#         token_data = TokenData(scopes=token_scopes, email=email)
#     except (JWTError, ValidationError):
#         raise credentials_exception

#     user = await users.get_by_email(session, token_data.email)
#     if user is None:
#         raise credentials_exception

#     # Scopes
#     for scope in security_scopes.scopes:
#         if scope not in token_data.scopes:
#             raise HTTPException(
#                 status_code = status.HTTP_401_UNAUTHORIZED,
#                 detail = "Not enough permissions",
#                 headers = {"WWW-Authenticate": authenticate_value})

#     return user


# async def get_current_user_full(
#     security_scopes: SecurityScopes,
#     session: AsyncSession = Depends(get_session),
#     token: str = Depends(oauth2_scheme),
# ) -> UserFullResponse:
#     """
#     Получение текущего пользователя по токену с ролями и правами
#     """

#     # Scopes
#     if security_scopes.scopes:
#         authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
#     else:
#         authenticate_value = "Bearer"
#     credentials_exception = HTTPException(
#         status_code = status.HTTP_401_UNAUTHORIZED,
#         detail = "Credentials are not valid",
#         headers = {"WWW-Authenticate": authenticate_value})

#     if await is_token_blacklisted(session, token):
#         raise credentials_exception

#     try:
#         payload = decode_access_token(token)

#         if payload is None:
#             raise credentials_exception

#         email: Optional[str] = payload.get("sub")  # type: ignore
#         if email is None:
#             raise credentials_exception

#         # Scopes
#         token_scopes: List[str] = payload.get("scopes", [])  # type: ignore

#         token_data = TokenData(scopes=token_scopes, email=email)
#     except (JWTError, ValidationError):
#         raise credentials_exception

#     user = await users.get_full_user_by_email(session, token_data.email)
#     if user is None:
#         raise credentials_exception

#     # Scopes
#     for scope in security_scopes.scopes:
#         if scope not in token_data.scopes:
#             raise HTTPException(
#                 status_code = status.HTTP_401_UNAUTHORIZED,
#                 detail = "Not enough permissions",
#                 headers = {"WWW-Authenticate": authenticate_value})

#     return user


# async def get_current_user_email(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)) -> str:
#     """
#     Получение текущего пользователя по почте
#     """

#     if await is_token_blacklisted(session, token):
#         raise CREDENTIALS_EXCEPTION

#     try:
#         payload = decode_access_token(token)

#         if payload is None:
#             raise CREDENTIALS_EXCEPTION

#         email: str = payload.get("sub")  # type: ignore
#         if email is None:
#             raise CREDENTIALS_EXCEPTION
#     except JWTError:
#         raise CREDENTIALS_EXCEPTION

#     if await validate_email(session, email):
#         return email

#     raise CREDENTIALS_EXCEPTION


# async def get_current_user_token(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)) -> str:
#     """
#     Получение токена текущего пользователя с валидацией токена
#     """

#     _ = await get_current_user_email(session, token)
#     return token


# async def reset_user_password(session: AsyncSession, email: str) -> bool:
#     """
#     Сброс пароля пользователя
#     """

#     alphabet = string.ascii_letters + string.digits + "!@#$%^&*"

#     while True:
#         password = "".join(secrets.choice(alphabet) for _ in range(16))
#         if (
#             any(c.islower() for c in password)
#             and any(c.isupper() for c in password)
#             and sum(c.isdigit() for c in password) >= 3
#         ):
#             break

#     item = UserUpdate(password=password)

#     query = await session.execute(UPDATE_USER(email=email, item=item))
#     result = query.one_or_none()

#     if result is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with email not found")

#     query = await session.execute(AUTH_RESET_PASSWORD(email))
#     result = query.one_or_none()

#     if result is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company or company supervisor not found")

#     item = UserResetPasswordEmail(**dict(result), user_password=password)
#     result = send_email_reset_password(item)

#     if not result:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email send error")

#     await session.commit()

#     return result


# def send_email_reset_password(item: UserResetPasswordEmail) -> bool:
#     """
#     Отправка письма сброса пароля
#     """

#     # Читаем шаблон (NOTE: по идее бы использовать Jinja2)
#     with open(os.path.join("app", "templates", "reset_password.html"), mode="r", encoding="utf-8") as f:
#         html = f.read()

#     html = html.replace("{{ item.sv_name }}", item.sv_name).replace("{{ item.user_name }}", item.user_name).replace(
#         "{{ item.user_login }}", item.user_login).replace("{{ item.user_password }}", item.user_password)

#     # Create message container - the correct MIME type is multipart/alternative.
#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = f"Восстановление пароля сотруднику {item.user_name}"
#     msg["From"] = EMAIL_LOGIN
#     msg["To"] = item.sv_email

#     # Record the MIME types of both parts - text/plain and text/html.
#     # part1 = MIMEText(text, "plain")
#     html_part = MIMEText(html, "html")

#     # Attach parts into message container.
#     # According to RFC 2046, the last part of a multipart message, in this case
#     # the HTML message, is best and preferred.
#     # msg.attach(part1)
#     msg.attach(html_part)

#     # Устанавливаем соединение
#     server = smtplib.SMTP_SSL(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT)

#     server.login(EMAIL_LOGIN, str(EMAIL_PASSWORD))

#     # message = "\r\n".join([
#     #     f"From: {EMAIL_LOGIN}",
#     #     f"To: {item.sv_email}",
#     #     f"Subject: Восстановление пароля сотруднику {item.user_name}",
#     #     "",
#     #     f"Здравствуйте, {item.sv_name}",
#     #     f"Ваш сотрудник {item.user_name} воспользовался сервисом сброса пароля на портале www.azkts.ru",
#     #     "",
#     #     f"Новые данные пользователя {item.user_name} для авторизации в систему:",
#     #     f"Логин: {item.user_login}",
#     #     f"Пароль: {item.user_password}",
#     # ]).encode("utf-8")

#     # Отправка
#     server.sendmail(EMAIL_LOGIN, item.sv_email, msg.as_bytes())
#     server.quit()

#     return True
