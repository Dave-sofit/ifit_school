import logging

from logging.handlers import TimedRotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from .config import settings
from .common.dependencies import setSession

from bot.handlers.common import router as commonRouter
from bot.handlers.courses import router as coursesRouter
from bot.handlers.admin import router as adminRouter

logHandler = TimedRotatingFileHandler(filename='logs/bot.log', when='D', interval=1, backupCount=0)
logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logHandler.setFormatter(logFormatter)
logHandler.setLevel(logging.INFO)
logging.basicConfig(handlers=[logHandler])

storage = RedisStorage.from_url(url=settings.REDIS_URI, connection_kwargs={'password': settings.REDIS_PASSWORD})
setSession()


async def main():
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    dp.include_routers(commonRouter)
    dp.include_routers(coursesRouter)
    dp.include_routers(adminRouter)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
