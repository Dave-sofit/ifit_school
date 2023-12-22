import logging
import locale

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from .config import settings
from .common.dependencies import setSession

# from .handlers import register_handlers_common,
# register_handlers_event, register_handlers_master, register_handlers_schedule
from bot.handlers.common import router as commonRouter
from bot.handlers.courses import router as coursesRouter

logger = logging.getLogger(__name__)

# Настройка логирования в stdout
logging.basicConfig(filename='bot.log', level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger.info("Starting bot")

storage = RedisStorage.from_url(url=settings.REDIS_URI, connection_kwargs={'password': settings.REDIS_PASSWORD})
setSession()


async def main():
    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    dp.include_routers(commonRouter)
    dp.include_routers(coursesRouter)

    # Регистрация хэндлеров
    # register_handlers_common(dp, settings.BOT_ADMIN_ID)
    # register_handlers_event(dp, settings.BOT_ADMIN_ID)
    # register_handlers_master(dp, settings.BOT_ADMIN_ID)
    # register_handlers_schedule(dp, settings.BOT_ADMIN_ID)
    locale.setlocale(locale.LC_ALL, locale="ru_RU.UTF-8")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
