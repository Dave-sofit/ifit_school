from json import loads

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from httpx import codes

from bot.common import ControlState
from bot.handlers.utils import updateUserCache, addBaseCommands, returnBack, setProductInCache
from bot.serviceObjects import ProductMng, ProductIn, CourseMng, CourseScheduleMng, CourseApplicationIn, \
    CourseApplicationMng
from bot.engine import cache

router = Router()


async def setBaseCommand(message: Message, state: FSMContext) -> None:
    await state.clear()
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Редагування курсів'))
    builder.add(KeyboardButton(text='Редагування співробітників'))
    builder.add(KeyboardButton(text='Повернутися назад'))
    builder.adjust(1)
    await state.set_state(ControlState.waitingControlObjectType)
    reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    await message.answer(text='Що будемо редагувати?', reply_markup=reply_markup)


async def getProducts(message: Message, state: FSMContext) -> Message:
    products = await ProductMng().getList(order_by={'order': {'data': 'order'}})
    builder = ReplyKeyboardBuilder()
    productsDict = {}
    for product in products:
        builder.add(KeyboardButton(text=f'{product.order}. {product.name}'))
        product_json = product.model_dump_json()
        productsDict.update({f'{product.order}.': product_json})

    await updateUserCache(user=message.from_user.id, value={'productsDict': productsDict})
    builder.add(KeyboardButton(text='Повернутися назад'))
    builder.adjust(2)
    await state.set_state(ControlState.waitingControlObject)
    reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    return await message.answer(text='Обери курс', reply_markup=reply_markup)


async def setProduct(message: Message, state: FSMContext) -> Message:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Опис курсу'))
    builder.add(KeyboardButton(text='Програма курсу'))
    builder.add(KeyboardButton(text='Міста'))
    builder.add(KeyboardButton(text='Сертифікат'))
    builder.add(KeyboardButton(text='Повернутись до вибору курсів'))
    builder.adjust(2)

    await state.set_state(ControlState.waitingAttribute)
    reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    return await message.answer(text='Що будемо редагувати?', reply_markup=reply_markup)


@router.message(F.text == 'Управління')
async def cmdAdmin(message: Message, state: FSMContext) -> None:
    await setBaseCommand(message=message, state=state)


@router.message(ControlState.waitingControlObjectType, F.text == 'Повернутися назад')
async def cmdReturnBack(message: Message, state: FSMContext) -> None:
    await returnBack(message=message, state=state)


@router.message(ControlState.waitingControlObject, F.text == 'Повернутися назад')
async def cmdReturnBack(message: Message, state: FSMContext) -> None:
    await setBaseCommand(message=message, state=state)


@router.message(ControlState.waitingControlObjectType, F.text == 'Редагування курсів')
async def cmdProducts(message: Message, state: FSMContext) -> None:
    await getProducts(message=message, state=state)


@router.message(ControlState.waitingAttribute, F.text == 'Повернутись до вибору курсів')
async def cmdAction(message: Message, state: FSMContext) -> None:
    await getProducts(message=message, state=state)


@router.message(ControlState.waitingControlObject)
async def cmdSetProduct(message: Message, state: FSMContext) -> None:
    product = await setProductInCache(message)
    if product is not None:
        await setProduct(message=message, state=state)


@router.message(ControlState.waitingAttribute, F.text == 'Опис курсу')
async def cmdAction(message: Message, state: FSMContext) -> None:
    await state.set_state(ControlState.waitingDescriptions)
    await message.answer(text='Введіть нове значення')


@router.message(ControlState.waitingDescriptions)
async def cmdAction(message: Message, state: FSMContext) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        product = loads(value).get('product')
        product.update(descriptions=message.text)
        await ProductMng().update(ProductIn(**product))
        await updateUserCache(user=message.from_user.id, value={'product': product})
        await message.answer(text=product.get('descriptions'))
        await setProduct(message=message, state=state)
