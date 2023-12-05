from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter

from bot.serviceObjects import UserMessengerMng, UserMng, UserIn, UserMessengerIn
from bot.common import MessengerTypes
from bot.handlers.utils import addBaseCommands

router = Router()


class AuthState(StatesGroup):
    waitingContact = State()


@router.message(CommandStart())
async def cmdStart(message: Message, state: FSMContext) -> None:
    # Если поступила данная команда, то сбрасываем предыдущее состояние
    await state.clear()

    # Проверяем авторизованн ли данный пользователь
    userMessenger = await UserMessengerMng().get(userMessengerId=message.from_user.id, noneable=True)
    if userMessenger is None:
        await state.set_state(AuthState.waitingContact)
        kbButton = [KeyboardButton(text='Отправить номер телефона', request_contact=True)]
        reply_markup = ReplyKeyboardMarkup(keyboard=[kbButton], resize_keyboard=True, one_time_keyboard=True)
        await message.answer(text='Представьтесь, отправьте контакт', reply_markup=reply_markup)
    else:
        # await message.answer(text='начнем!')
        await message.answer(text=f'{message.from_user.first_name} начнем!', reply_markup=await addBaseCommands())


@router.message(StateFilter(None), Command("cancel"))
async def cmdCancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Действие отменено', reply_markup=await addBaseCommands())


@router.message(AuthState.waitingContact)
async def cmdSetContact(message: Message, state: FSMContext) -> None:
    contact = message.contact
    if contact is not None and message.from_user.id == contact.user_id:
        phone = contact.phone_number.replace('+', '').replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
        user = await UserMng().first(phone=phone)
        if user is None:
            user = await UserMng().create(UserIn(firstName=contact.first_name, phone=phone))

        userMessenger = await UserMessengerMng().get(userMessengerId=contact.user_id, noneable=True)
        if userMessenger is None:
            await UserMessengerMng().create(UserMessengerIn(userMessengerId=contact.user_id, type=MessengerTypes.telegram,
                                                            userUid=user.uid))

        await message.answer(text=f'{message.from_user.first_name} номер получен, спасибо',
                             reply_markup=(await addBaseCommands()))
        await state.clear()
    else:
        await message.answer(text=f'{message.from_user.first_name} это не ваш номер')
        await state.clear()

# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.
# async def secretCommand(message: Message):
#     await message.answer('Поздравляю! Эта команда доступна только администратору бота.')


# def register_handlers_common(dp: Dispatcher, admin_id: int):
#     dp.register_message_handler(cmdStart, commands='start', state="*")
#     dp.register_message_handler(cmdCancel, commands='cancel', state="*")
#     dp.register_message_handler(cmdCancel, Text(equals='отмена', ignore_case=True), state='*')
#     dp.register_message_handler(cmdSetContact, content_types=['contact'], state="*")
#     dp.register_message_handler(secretCommand, IDFilter(user_id=admin_id), commands='abracadabra')
#     dp.register_message_handler(cmdCancel, Text(equals='Вернуться в главное меню', ignore_case=True), state='*')
