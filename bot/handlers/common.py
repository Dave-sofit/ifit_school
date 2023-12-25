from aiogram import Router
from aiogram.types import Message

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter

from bot.handlers.utils import addBaseCommands

router = Router()


@router.message(CommandStart())
async def cmdStart(message: Message, state: FSMContext) -> None:
    # # Если поступила данная команда, то сбрасываем предыдущее состояние
    await state.clear()
    await message.answer(text=f'{message.from_user.first_name} привіт, почнемо спілкування!',
                         reply_markup=await addBaseCommands())


@router.message(StateFilter(None), Command("cancel"))
async def cmdCancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Действие отменено', reply_markup=await addBaseCommands())
