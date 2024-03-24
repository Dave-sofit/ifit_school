from json import loads, dumps

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.engine import cache
from bot.config import settings


async def addBaseCommands(messengerId: int) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Базові курси навчання'))
    builder.add(KeyboardButton(text='Семінари та майстер-класи'))
    builder.add(KeyboardButton(text='Мої дані'))
    if messengerId == int(settings.BOT_ADMIN_ID):
        builder.add(KeyboardButton(text='Управління'))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


async def addCancelCommand():
    kbButton = [KeyboardButton(text='Повернутися до головного меню')]
    return ReplyKeyboardMarkup(keyboard=[kbButton], resize_keyboard=True, one_time_keyboard=True)


async def returnBack(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Вибери дію', reply_markup=await addBaseCommands(messengerId=message.from_user.id))


async def updateUserCache(user, value: dict) -> None:
    userCache = await cache.get(user)
    if userCache is None:
        userCacheDict = {}
    else:
        userCacheDict = loads(userCache)

    userCacheDict.update(value)
    await cache.set(user, dumps(userCacheDict))


async def setProductInCache(message: Message) -> dict | None:
    product = None
    userCache = await cache.get(message.from_user.id)
    if userCache is not None and len(message.text) > 2:
        productsDict = loads(userCache).get('productsDict')
        if productsDict is not None:
            value = productsDict.get(message.text[:2])
            if value is not None:
                product = loads(value)
                await updateUserCache(user=message.from_user.id, value={'product': product})

    return product
