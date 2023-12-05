from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def addBaseCommands():
    kbButton1 = [KeyboardButton(text='Базові курси навчання'), KeyboardButton(text='Семінари та майстер-класи')]
    kbButton2 = [KeyboardButton(text='Мои данные')]
    return ReplyKeyboardMarkup(keyboard=[kbButton1, kbButton2], resize_keyboard=True, one_time_keyboard=True)


async def addCancelCommand():
    kbButton = [KeyboardButton(text='Вернуться в главное меню')]
    return ReplyKeyboardMarkup(keyboard=[kbButton], resize_keyboard=True, one_time_keyboard=True)
