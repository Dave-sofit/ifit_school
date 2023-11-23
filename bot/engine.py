from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from bot.config import settings
from . import SessionData, emptyRef

engine = create_async_engine(settings.DATABASE_URI, pool_size=20, max_overflow=20, future=True, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)
cache = aioredis.from_url(settings.REDIS_URI, password=settings.REDIS_PASSWORD)


def getSession():  # -> Iterator[Session]:
    session = SessionData.session.get()
    if session and session != emptyRef:
        return session
    else:
        session = async_session()
        SessionData.session.set(session)
        return session
