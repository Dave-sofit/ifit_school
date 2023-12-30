from json import loads
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from httpx import codes

from bot.common import InformingState
from bot.serviceObjects import ProductMng, CourseMng, CourseScheduleMng, CourseApplicationIn, CourseApplicationMng, \
    UserMng, UserIn
from bot.serviceObjects.crmConnector import Order, SenderOrder
from bot.engine import cache
from bot.handlers.utils import updateUserCache, addBaseCommands

router = Router()


async def getProducts(message: Message, state: FSMContext) -> Message:
    await state.clear()
    products = await ProductMng().getList()
    builder = ReplyKeyboardBuilder()
    for i in range(len(products)):
        products[i].order = i + 1
        product_json = products[i].model_dump_json()
        await cache.set(f'{products[i].order}.', product_json)
        builder.add(KeyboardButton(text=f'{products[i].order}. {products[i].name}'))

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
    product = loads(userCache).get('product')
    order = product.get('order')
    courses = await CourseMng().getList(**{'data': {'productUid': product.get('uid')}})
    builder = ReplyKeyboardBuilder()
    for i in range(len(courses)):
        builder.add(KeyboardButton(text=f'{order}.{i + 1} {courses[i].name}'))
        course_json = courses[i].model_dump_json()
        await cache.set(f'{order}.{i + 1}', course_json)

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

    courseSchedule = await CourseScheduleMng().getList(**{'courseUid': course.get('uid')})
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
async def cmdSetProduct(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text='Вибери дію', reply_markup=await addBaseCommands())


@router.message(InformingState.waitingProduct)
async def cmdSetProduct(message: Message, state: FSMContext) -> None:
    if len(message.text) > 2:
        value = await cache.get(message.text[:2])
        if value is not None:
            product = loads(value)
            await updateUserCache(user=message.from_user.id, value={'product': product})
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
    value = await cache.get(message.from_user.id)
    if value is not None:
        await getCourses(message=message, state=state, userCache=value)


@router.message(InformingState.waitingAction, F.text == 'Опис курсу')
async def cmdAction(message: Message) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        product = loads(value).get('product')
        await message.answer(text=product.get('descriptions'))


@router.message(InformingState.waitingAction, F.text == 'Програма курсу')
async def cmdAction(message: Message) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        product = loads(value).get('product')
        await message.answer(text=product.get('content'))


@router.message(InformingState.waitingAction, F.text == 'Сертифікат')
async def cmdAction(message: Message) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        product = loads(value).get('product')
        await message.answer(text=product.get('certificate'))


@router.message(InformingState.waitingAction, F.text == 'Як проходить навчання')
async def cmdAction(message: Message, state: FSMContext) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        await getCourses(message=message, state=state, userCache=value)


@router.message(InformingState.waitingPlace)
async def cmdSetDetail(message: Message, state: FSMContext) -> None:
    if len(message.text) > 3:
        value = await cache.get(message.text[:3])
        if value is not None:
            course = loads(value)
            await updateUserCache(user=message.from_user.id, value={'course': course})
            await setDetail(message=message, state=state, course=course)


@router.message(InformingState.waitingDetails, F.text == 'Основне')
async def cmdAction(message: Message, state: FSMContext) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        course = loads(value).get('course')
        await setDetail(message=message, state=state, course=course)


@router.message(InformingState.waitingDetails, F.text == 'Навчальний процес')
async def cmdAction(message: Message) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        course = loads(value).get('course')
        section = course.get('descriptions')
        await message.answer(text=f'<b><u>Навчальний процес</u></b>\n{section}')


@router.message(InformingState.waitingDetails, F.text == 'Iспит та акредитація')
async def cmdAction(message: Message) -> None:
    value = await cache.get(message.from_user.id)
    if value is not None:
        course = loads(value).get('course')
        section = course.get('exam')
        await message.answer(text=f'<b><u>Iспит та акредитація</u></b>\n{section}')


@router.callback_query(F.data.startswith('select_date_'))
async def callbacksSelectDate(callback: CallbackQuery) -> None:
    user = await UserMng().get(userMessengerId=callback.from_user.id, noneable=True)
    if user is None:
        kbButton = [KeyboardButton(text='Надіслати контакт', request_contact=True)]
        reply_markup = ReplyKeyboardMarkup(keyboard=[kbButton], resize_keyboard=True, one_time_keyboard=True)
        await callback.message.answer(text='Представтеся', reply_markup=reply_markup)
        await callback.answer()
    else:
        dateStr = callback.data.split('_')[-1]
        date = datetime.strptime(dateStr, '%d-%m-%Y')
        value = await cache.get(callback.from_user.id)
        if value is not None:
            course = loads(value).get('course')
            productName = loads(value).get('product').get('name')
            courseApplication = await CourseApplicationMng().create(
                CourseApplicationIn(userUid=user.uid, courseUid=course.get('uid'), startDate=date))

            order = Order(user=courseApplication.user, course=courseApplication.course, startDate=date)
            response = await SenderOrder.sendToCrm(obj=order)

            if response.status_code == codes.OK:
                await callback.message.answer(text=f'Вашу заявку на курс {productName} / {dateStr} зареєстровано')
            else:
                await callback.message.answer(text=f'Не вдалося залишити заявку на курс {productName} / {dateStr}')

            await callback.answer()


@router.message(F.contact)
async def cmdSetContact(message: Message) -> None:
    contact = message.contact
    if contact is not None and message.from_user.id == contact.user_id:
        phone = contact.phone_number.replace('+', '').replace('-', '').replace('(', '').replace(')', '').replace(' ',
                                                                                                                 '')
        user = await UserMng().first(phone=phone)
        if user is None:
            user = await UserMng().create(
                UserIn(firstName=contact.first_name, phone=phone, messengerId=contact.user_id))

        await message.answer(text=f'{message.from_user.first_name} номер отриманий, дякую',
                             reply_markup=(await addBaseCommands()))

        await updateUserCache(user=message.from_user.id, value={'user': user.model_dump_json()})
    else:
        await message.answer(text=f'{message.from_user.first_name} це не ваш номер')

    await message.answer(text=f'Повторіть спробу запису на курс', reply_markup=await addDetailsCommands())
