from sqlalchemy import text

from bot.engine import engine
from bot.models.utils import Base


async def async_main():
    async with engine.begin() as conn:
        await conn.execute(text('DROP TABLE IF EXISTS "usersList" CASCADE'))

        await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

