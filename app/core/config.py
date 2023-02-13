from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

# Debug mode, NOTE: Debug panel cause memory leaking over time
TESTING = config("TESTING", cast=bool, default=False)

# BOT
BOT_TOKEN = config("BOT_TOKEN", cast=str)
RANDOM_IMAGE_API = config("RANDOM_IMAGE_API", cast=str)
USER_CREATE_URL = config("USER_CREATE_URL", cast=str)
GET_USERS_URL = config("GET_USERS_URL", cast=str)
BASE_URL = config("BASE_URL", cast=str)
GET_COMPANIES = config("GET_COMPANIES", cast=str)

# DB
DB_HOST = config("DB_HOST", cast=str, default="localhost")
DB_PORT = config("DB_PORT", cast=int, default=5432)
DB_NAME = config("DB_NAME", cast=str, default="")
DB_USER = config("DB_USER", cast=str, default="")
DB_PASSWORD = config("DB_PASSWORD", cast=str, default="")
DB_ASYNC = True

DATABASE_URL = (
    f"postgresql{'+asyncpg' if DB_ASYNC else ''}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    if not TESTING else
    f"postgresql{'+asyncpg' if DB_ASYNC else ''}://testing:testing@{DB_HOST}:{DB_PORT}/testing"
)

WORKER_ID = config("WORKER_ID", cast=int, default=0)
PROCESS_ID = config("PROCESS_ID", cast=int, default=0)

API_VERSION = 1

# Authorizing
JWT_SECRET_KEY = config("JWT_SECRET_KEY", cast=Secret, default="")
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
JWT_EXPIRE_MINUTES = config("JWT_EXPIRE_MINUTES", cast=int, default=60)
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = config("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", cast=int, default=60 * 24 * 30)
