from json import loads
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from httpx import codes

from bot.common import InformingState
from bot.serviceObjects import ProductMng, CourseMng, CourseScheduleMng, CourseApplicationIn, CourseApplicationMng
from bot.serviceObjects.crmConnector import Order, SenderOrder
from bot.engine import cache
from bot.handlers.utils import updateCache, returnBack, setProductInCache

router = Router()


async def getProducts(message: Message, state: FSMContext) -> Message:
    await state.clear()
    products = await ProductMng().getList(order_by={'order': {'data': 'order'}})
    builder = ReplyKeyboardBuilder()
    productsDict = {}
    for product in products:
        builder.add(KeyboardButton(text=f'{product.order}. {product.name}'))
        product_json = product.model_dump_json()
        productsDict.update({f'{product.order}.': product_json})

    await updateCache(key=f'{message.from_user.id}_productsDict', value=productsDict)
    builder.add(KeyboardButton(text='Повернутися назад'))
    builder.adjust(2)
    await state.set_state(InformingState.waitingProduct)
    reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    return await message.answer(text='Обери курс', reply_markup=reply_markup)


async def setProduct(message: Message, state: FSMContext, text: str) -> Message:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Опис курсу'))
    builder.add(KeyboardButton(text='Програма курсу'))
    builder.add(KeyboardButton(text='Як проходить навчання'))
    builder.add(KeyboardButton(text='Сертифікат'))
    builder.add(KeyboardButton(text='Повернутись до вибору курсів'))
    builder.adjust(2)

    await state.set_state(InformingState.waitingAction)
    reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    return await message.answer(text=text, reply_markup=reply_markup)


async def getCourses(message: Message, state: FSMContext, userCache: str) -> Message:
    product = loads(userCache)
    order = product.get('order')
    courses = await CourseMng().getList(order_by={'order': {'data': 'order'}},
                                        **{'data': {'productUid': product.get('uid')}})
    builder = ReplyKeyboardBuilder()
    coursesDict = {}
    for i in range(len(courses)):
        builder.add(KeyboardButton(text=f'{order}.{i + 1} {courses[i].name}'))
        course_json = courses[i].model_dump_json()
        coursesDict.update({f'{order}.{i + 1}': course_json})

    await updateCache(key=f'{message.from_user.id}_coursesDict', value=coursesDict)
    builder.add(KeyboardButton(text='Повернутись до курсу'))
    builder.adjust(2)
    await state.set_state(InformingState.waitingPlace)
    return await message.answer(text='Вибери місто',
                                reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=False))


async def setDetail(message: Message, state: FSMContext, course: dict) -> Message:
    employees = course.get('employees')
    textEmployees = '<b><u>Викладачі:</u></b>\n'
    for employee in employees:
        fullName = employee.get('fullName')
        textEmployees += f'{fullName}\n'

    location = course.get('location')
    textLocation = f'<b><u>Адреса:</u></b>\n{location}\n'

    price = course.get('price')
    textPrice = f'<b><u>Вартість</u></b>: {price} грн\n'

    textSchedule = '<b><u>Розклад:</u></b>\n'

    courseSchedule = await CourseScheduleMng().getList(order_by={'order': 'startDate'},
                                                       **{'courseUid': course.get('uid')})
    builder = InlineKeyboardBuilder()
    for row in courseSchedule:
        startDate = row.startDate.strftime('%d-%m-%Y')
        builder.add(InlineKeyboardButton(text=f'{startDate}', callback_data=f'select_date_{startDate}'))

    builder.adjust(2)
    await message.answer(text=f'{textEmployees}\n{textLocation}\n{textPrice}\n{textSchedule}\nЗаписатися на курс з',
                         reply_markup=builder.as_markup(resize_keyboard=True))

    await state.set_state(InformingState.waitingDetails)
    reply_markup = await addDetailsCommands()
    return await message.answer(text=f'Вибери дію', reply_markup=reply_markup)


async def addDetailsCommands() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Основне'))
    builder.add(KeyboardButton(text='Навчальний процес'))
    builder.add(KeyboardButton(text='Iспит та акредитація'))
    builder.add(KeyboardButton(text='Повернутись до вибору місто'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


@router.message(F.text == 'Базові курси навчання')
async def cmdProducts(message: Message, state: FSMContext) -> None:
    await getProducts(message=message, state=state)


@router.message(InformingState.waitingProduct, F.text == 'Повернутися назад')
async def cmdReturnBack(message: Message, state: FSMContext) -> None:
    await returnBack(message=message, state=state)


@router.message(InformingState.waitingProduct)
async def cmdSetProduct(message: Message, state: FSMContext) -> None:
    product = await setProductInCache(message)
    if product is not None:
        text = product.get('descriptions')
        await setProduct(message=message, state=state, text=text)


@router.message(InformingState.waitingAction, F.text == 'Повернутись до вибору курсів')
async def cmdAction(message: Message, state: FSMContext) -> None:
    await getProducts(message=message, state=state)


@router.message(InformingState.waitingPlace, F.text == 'Повернутись до курсу')
async def cmdDetails(message: Message, state: FSMContext) -> None:
    await setProduct(message=message, state=state, text='Вибери дію')


@router.message(InformingState.waitingDetails, F.text == 'Повернутись до вибору місто')
async def cmdDetails(message: Message, state: FSMContext) -> None:
    userCache = await cache.get(f'{message.from_user.id}_product')
    if userCache is not None:
        await getCourses(message=message, state=state, userCache=userCache)


@router.message(InformingState.waitingAction, F.text == 'Опис курсу')
async def cmdAction(message: Message) -> None:
    userCache = await cache.get(f'{message.from_user.id}_product')
    if userCache is not None:
        product = loads(userCache)
        await message.answer(text=product.get('descriptions'))


@router.message(InformingState.waitingAction, F.text == 'Програма курсу')
async def cmdAction(message: Message) -> None:
    userCache = await cache.get(f'{message.from_user.id}_product')
    if userCache is not None:
        product = loads(userCache)
        await message.answer(text=product.get('content'))


@router.message(InformingState.waitingAction, F.text == 'Сертифікат')
async def cmdAction(message: Message) -> None:
    userCache = await cache.get(f'{message.from_user.id}_product')
    if userCache is not None:
        product = loads(userCache)
        await message.answer(text=product.get('certificate'))


@router.message(InformingState.waitingAction, F.text == 'Як проходить навчання')
async def cmdAction(message: Message, state: FSMContext) -> None:
    userCache = await cache.get(f'{message.from_user.id}_product')
    if userCache is not None:
        await getCourses(message=message, state=state, userCache=userCache)


@router.message(InformingState.waitingPlace)
async def cmdSetDetail(message: Message, state: FSMContext) -> None:
    userCache = await cache.get(f'{message.from_user.id}_coursesDict')
    if userCache is not None and len(message.text) > 3:
        coursesDict = loads(userCache)
        if coursesDict is not None:
            value = coursesDict.get(message.text[:3])
            if value is not None:
                course = loads(value)
                await updateCache(key=f'{message.from_user.id}_course', value=course)
                await setDetail(message=message, state=state, course=course)


@router.message(InformingState.waitingDetails, F.text == 'Основне')
async def cmdAction(message: Message, state: FSMContext) -> None:
    value = await cache.get(f'{message.from_user.id}_course')
    if value is not None:
        course = loads(value)
        await setDetail(message=message, state=state, course=course)


@router.message(InformingState.waitingDetails, F.text == 'Навчальний процес')
async def cmdAction(message: Message) -> None:
    value = await cache.get(f'{message.from_user.id}_course')
    if value is not None:
        course = loads(value)
        section = course.get('descriptions')
        await message.answer(text=f'<b><u>Навчальний процес</u></b>\n{section}')


@router.message(InformingState.waitingDetails, F.text == 'Iспит та акредитація')
async def cmdAction(message: Message) -> None:
    value = await cache.get(f'{message.from_user.id}_course')
    if value is not None:
        course = loads(value)
        section = course.get('exam')
        await message.answer(text=f'<b><u>Iспит та акредитація</u></b>\n{section}')


@router.callback_query(F.data.startswith('select_date_'))
async def callbacksSelectDate(callback: CallbackQuery) -> None:
    dateStr = callback.data.split('_')[-1]
    date = datetime.strptime(dateStr, '%d-%m-%Y')

    user = loads(await cache.get(f'{callback.from_user.id}_user'))
    course = loads(await cache.get(f'{callback.from_user.id}_course'))
    productName = loads(await cache.get(f'{callback.from_user.id}_product')).get('name')

    courseApplication = await CourseApplicationMng().create(
        CourseApplicationIn(userUid=user.get('uid'), courseUid=course.get('uid'), startDate=date))

    order = Order(user=courseApplication.user, course=courseApplication.course, startDate=date)
    response = await SenderOrder.sendToCrm(obj=order)

    if response.status_code == codes.OK:
        await callback.message.answer(text=f'Вашу заявку на курс {productName} / {dateStr} зареєстровано')
    else:
        await callback.message.answer(text=f'Не вдалося залишити заявку на курс {productName} / {dateStr}')

    await callback.answer()
