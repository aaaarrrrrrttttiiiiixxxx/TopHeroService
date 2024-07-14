import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '../', '.env'))

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

# SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_DATABASE_URL = f"postgresql://top_hero_service:vc894hv9w@127.0.0.1:5432/top_hero_service"
SQLALCHEMY_DATABASE_ASYNC_URL = f"postgresql+asyncpg://top_hero_service:vc894hv9w@127.0.0.1:5432/top_hero_service"

async_engine = create_async_engine(SQLALCHEMY_DATABASE_ASYNC_URL, echo=True)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
engine = create_engine(SQLALCHEMY_DATABASE_URL)


async def generate_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        return session


def get_session() -> Session:
    with Session(engine) as session:
        yield session


Base = declarative_base()
