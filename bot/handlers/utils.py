from json import loads, dumps

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.engine import cache


async def addBaseCommands() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Базові курси навчання'))
    builder.add(KeyboardButton(text='Семінари та майстер-класи'))
    builder.add(KeyboardButton(text='Мої дані'))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


async def addCancelCommand():
    kbButton = [KeyboardButton(text='Повернутися до головного меню')]
    return ReplyKeyboardMarkup(keyboard=[kbButton], resize_keyboard=True, one_time_keyboard=True)


async def updateUserCache(user, value: dict) -> None:
    userCacheDict = loads(await cache.get(user))
    userCacheDict.update(value)
    await cache.set(user, dumps(userCacheDict))
