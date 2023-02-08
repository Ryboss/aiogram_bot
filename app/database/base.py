from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base

from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, poolclass=NullPool)

Base = declarative_base()
Session = sessionmaker(engine)
