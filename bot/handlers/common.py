from aiogram import Router, F
from aiogram.types import Message

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.handlers.utils import addBaseCommands, updateCache
from bot.serviceObjects import UserMng, UserIn

router = Router()


@router.message(CommandStart())
async def cmdStart(message: Message, state: FSMContext) -> None:
    # # Если поступила данная команда, то сбрасываем предыдущее состояние
    await state.clear()
    user = await UserMng().first(data={'messengerId': message.from_user.id})
    if user is None:
        kbButton = [KeyboardButton(text='Надіслати контакт', request_contact=True)]
        reply_markup = ReplyKeyboardMarkup(keyboard=[kbButton], resize_keyboard=True, one_time_keyboard=True)
        await message.answer(text='Уявіть, натисніть кнопку надіслати контакт', reply_markup=reply_markup)
    else:
        await message.answer(text=f'{message.from_user.first_name} привіт, почнемо спілкування!',
                             reply_markup=await addBaseCommands(messengerId=message.from_user.id))


@router.message(Command("help"))
async def cmdCancel(message: Message) -> None:
    await message.answer('Якщо раптом зникли кнопки, то натисніть на цю іконку &#127899;')


@router.message(F.contact)
async def cmdSetContact(message: Message) -> None:
    contact = message.contact
    if contact is not None and message.from_user.id == contact.user_id:
        phone = contact.phone_number.replace('+', '').replace('-', '').replace('(', '').replace(')', '').replace(' ',
                                                                                                                 '')
        user = await UserMng().first(** {'data': {'phone': phone}})
        if user is None:
            user = await UserMng().create(
                UserIn(firstName=contact.first_name, phone=phone, messengerId=contact.user_id))

        await message.answer(text=f'{message.from_user.first_name} номер отриманий, дякую',
                             reply_markup=(await addBaseCommands(messengerId=message.from_user.id)))

        await updateCache(key=f'{message.from_user.id}_user', value=user.model_dump())
    else:
        await message.answer(text=f'{message.from_user.first_name} це не ваш номер')
