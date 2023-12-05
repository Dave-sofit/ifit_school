from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter

from bot.serviceObjects import UserMessengerMng
from bot.common import MessengerTypes
from bot.handlers.utils import addBaseCommands

router = Router()


@router.message(F.text == 'Базові курси навчання')
async def cmdCourses(message: Message) -> None:
    kbButton1 = [KeyboardButton(text='Інструктор групових програм EQF-3'),
                 KeyboardButton(text='Інструктор тренажерного залу EQF-3')]
    kbButton2 = [KeyboardButton(text='Персональний тренер EQF-4'),
                 KeyboardButton(text='Дієтолог-нутріціолог')]
    reply_markup = ReplyKeyboardMarkup(keyboard=[kbButton1, kbButton2], resize_keyboard=True, one_time_keyboard=True)
    await message.answer(text='Представьтесь, отправьте контакт', reply_markup=reply_markup)
