from json import loads
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from bot.common import ControlState
from bot.handlers.utils import updateCache, returnBack, setProductInCache
from bot.serviceObjects import ProductMng, ProductUpdate, CourseMng, CourseUpdate, CourseScheduleMng, CourseScheduleIn
from bot.serviceObjects import SimpleCalendar, SimpleCalendarCallback
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

    await updateCache(key=f'{message.from_user.id}_productsDict', value=productsDict)
    builder.add(KeyboardButton(text='Повернутися назад'))
    builder.adjust(2)
    await state.set_state(ControlState.waitingControlObject)
    reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    return await message.answer(text='Обери курс', reply_markup=reply_markup)


async def setProduct(message: Message, state: FSMContext) -> Message:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Опис курсу'))
    builder.add(KeyboardButton(text='Програма курсу'))
    builder.add(KeyboardButton(text='Як проходить навчання'))
    builder.add(KeyboardButton(text='Сертифікат'))
    builder.add(KeyboardButton(text='Повернутись до вибору курсів'))
    builder.adjust(2)

    await state.set_state(ControlState.waitingAttribute)
    reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    return await message.answer(text='Що будемо редагувати?', reply_markup=reply_markup)


async def updateProduct(message: Message, state: FSMContext, updateValue: dict) -> None:
    value = await cache.get(f'{message.from_user.id}_product')
    if value is not None:
        product = loads(value)
        product.update(updateValue)
        await ProductMng().update(ProductUpdate(**product))
        await updateCache(key=f'{message.from_user.id}_product', value=product)
        await message.answer(text='Дані оновлено')
        await setProduct(message=message, state=state)


async def updateCourse(message: Message, state: FSMContext, updateValue: dict) -> None:
    value = await cache.get(f'{message.from_user.id}_course')
    if value is not None:
        course = loads(value)
        course.update(updateValue)
        await CourseMng().update(CourseUpdate(**course))
        await updateCache(key=f'{message.from_user.id}_course', value=course)
        await message.answer(text='Дані оновлено')
        await setCourse(message=message, state=state)


async def commandsUpdateValue(message: Message, state: FSMContext, newState: State, attrName: str) -> None:
    if newState == ControlState.waitingCourseDescriptions:
        value = await cache.get(f'{message.from_user.id}_course')
    else:
        value = await cache.get(f'{message.from_user.id}_product')

    if value is not None:
        product = loads(value)
        attr = product.get(attrName)
    else:
        attr = ''

    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Скасувати'))
    builder.adjust(2)
    await state.set_state(newState)
    await message.answer(text=f'Поточне значення:\n{attr}\n\nВведіть нове значення',
                         reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True))


async def getCourses(message: Message, state: FSMContext) -> Message:
    value = await cache.get(f'{message.from_user.id}_product')
    if value is not None:
        product = loads(value)
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
        await state.set_state(ControlState.waitingPlace)
        return await message.answer(text='Вибери місто',
                                    reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True))


async def setCourse(message: Message, state: FSMContext) -> Message:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Навчальний процес'))
    builder.add(KeyboardButton(text='Iспит та акредитація'))
    builder.add(KeyboardButton(text='Адреса'))
    builder.add(KeyboardButton(text='Розклад'))
    # builder.add(KeyboardButton(text='Вартість'))
    builder.add(KeyboardButton(text='Повернутись до вибору місто'))
    builder.adjust(2)

    await state.set_state(ControlState.waitingCourseAttribute)
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
async def cmdUpdateProducts(message: Message, state: FSMContext) -> None:
    await getProducts(message=message, state=state)


@router.message(ControlState.waitingAttribute, F.text == 'Повернутись до вибору курсів')
async def cmdGetProducts(message: Message, state: FSMContext) -> None:
    await getProducts(message=message, state=state)


@router.message(ControlState.waitingControlObject)
async def cmdSetProduct(message: Message, state: FSMContext) -> None:
    product = await setProductInCache(message)
    if product is not None:
        await setProduct(message=message, state=state)


@router.message(ControlState.waitingAttribute, F.text == 'Опис курсу')
async def cmdDescription(message: Message, state: FSMContext) -> None:
    await commandsUpdateValue(message=message, state=state, newState=ControlState.waitingDescriptions,
                              attrName='descriptions')


@router.message(ControlState.waitingAttribute, F.text == 'Програма курсу')
async def cmdContent(message: Message, state: FSMContext) -> None:
    await commandsUpdateValue(message=message, state=state, newState=ControlState.waitingContent, attrName='content')


@router.message(ControlState.waitingAttribute, F.text == 'Сертифікат')
async def cmdCertificate(message: Message, state: FSMContext) -> None:
    await commandsUpdateValue(message=message, state=state, newState=ControlState.waitingCertificate,
                              attrName='certificate')


@router.message(ControlState.waitingAttribute, F.text == 'Як проходить навчання')
async def cmdCourses(message: Message, state: FSMContext) -> None:
    await getCourses(message=message, state=state)


@router.message((F.text == 'Скасувати') | (F.text == 'Повернутись до курсу'))
async def cmdCancel(message: Message, state: FSMContext) -> None:
    if (state == ControlState.waitingCourseLocation or state == ControlState.waitingCoursePrice
            or state == ControlState.waitingCourseExam or state == ControlState.waitingCourseDescriptions):
        await setCourse(message=message, state=state)
    else:
        await setProduct(message=message, state=state)


@router.message(ControlState.waitingDescriptions)
async def cmdUpdateDescription(message: Message, state: FSMContext) -> None:
    updateValue = {'descriptions': message.html_text}
    await updateProduct(message=message, state=state, updateValue=updateValue)


@router.message(ControlState.waitingContent)
async def cmdUpdateContent(message: Message, state: FSMContext) -> None:
    updateValue = {'content': message.html_text}
    await updateProduct(message=message, state=state, updateValue=updateValue)


@router.message(ControlState.waitingCertificate)
async def cmdUpdateCertificate(message: Message, state: FSMContext) -> None:
    updateValue = {'certificate': message.html_text}
    await updateProduct(message=message, state=state, updateValue=updateValue)


@router.message(ControlState.waitingPlace)
async def cmdSetDetail(message: Message, state: FSMContext) -> None:
    userCache = await cache.get(f'{message.from_user.id}_coursesDict')
    if userCache is not None and len(message.text) > 3:
        coursesDict = loads(userCache)
        if coursesDict is not None:
            value = coursesDict.get(message.text[:3])
            if value is not None:
                course = loads(value)
                await updateCache(key=f'{message.from_user.id}_course', value=course)
                await setCourse(message=message, state=state)


@router.message(F.text == 'Повернутись до вибору місто')
async def cmdCancel(message: Message, state: FSMContext) -> None:
    await getCourses(message=message, state=state)


@router.message(ControlState.waitingCourseAttribute, F.text == 'Навчальний процес')
async def cmdDescription(message: Message, state: FSMContext) -> None:
    await commandsUpdateValue(message=message, state=state, newState=ControlState.waitingCourseDescriptions,
                              attrName='descriptions')


@router.message(ControlState.waitingCourseAttribute, F.text == 'Iспит та акредитація')
async def cmdContent(message: Message, state: FSMContext) -> None:
    await commandsUpdateValue(message=message, state=state, newState=ControlState.waitingCourseExam, attrName='exam')


@router.message(ControlState.waitingCourseAttribute, F.text == 'Адреса')
async def cmdCertificate(message: Message, state: FSMContext) -> None:
    await commandsUpdateValue(message=message, state=state, newState=ControlState.waitingCourseLocation,
                              attrName='location')


@router.message(ControlState.waitingCourseAttribute, F.text == 'Розклад')
async def cmdDate(message: Message, state: FSMContext) -> None:
    value = await cache.get(f'{message.from_user.id}_course')
    if value is not None:
        course = loads(value)
        courseSchedule = await CourseScheduleMng().getList(order_by={'order': 'startDate'},
                                                           **{'courseUid': course.get('uid')})
        builder = InlineKeyboardBuilder()
        for row in courseSchedule:
            startDate = row.startDate.strftime('%d-%m-%Y')
            builder.add(InlineKeyboardButton(text=f'{startDate} - Видалити', callback_data=f'delete_date_{startDate}'))

        builder.adjust(2)
        await message.answer(text=f'Дата проведення курсу',
                             reply_markup=builder.as_markup(resize_keyboard=True))

        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text='Додати дату'))
        builder.add(KeyboardButton(text='Скасувати додавання дати'))
        builder.adjust(1)

        await state.set_state(ControlState.waitingCourseDate)
        reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
        await message.answer(text='Бажаєте додати дату?', reply_markup=reply_markup)


@router.message(ControlState.waitingCourseDescriptions)
async def cmdUpdateDescription(message: Message, state: FSMContext) -> None:
    updateValue = {'descriptions': message.html_text}
    await updateCourse(message=message, state=state, updateValue=updateValue)


@router.message(ControlState.waitingCourseExam)
async def cmdUpdateDescription(message: Message, state: FSMContext) -> None:
    updateValue = {'exam': message.html_text}
    await updateCourse(message=message, state=state, updateValue=updateValue)


@router.message(ControlState.waitingCourseLocation)
async def cmdUpdateDescription(message: Message, state: FSMContext) -> None:
    updateValue = {'location': message.html_text}
    await updateCourse(message=message, state=state, updateValue=updateValue)


@router.callback_query(F.data.startswith('delete_date_'))
async def callbacksDeleteDate(callback: CallbackQuery, state: FSMContext) -> None:
    dateStr = callback.data.split('_')[-1]
    date = datetime.strptime(dateStr, '%d-%m-%Y')
    value = await cache.get(f'{callback.from_user.id}_course')
    if value is not None:
        course = loads(value)
        courseScheduleIn = CourseScheduleIn(courseUid=course.get('uid'), startDate=date)
        await CourseScheduleMng().delete(courseScheduleIn)

    await callback.message.answer(text=f'Ви видалити {date.strftime("%d/%m/%Y")}')
    await callback.answer()
    await setCourse(message=callback.message, state=state)


@router.message(F.text == 'Скасувати додавання дати')
async def cmdCancelAddDate(message: Message, state: FSMContext) -> None:
    await setCourse(message=message, state=state)


@router.message(ControlState.waitingCourseDate)
async def cmdAddDate(message: Message) -> None:
    await message.answer(
        'Будь ласка, виберіть дату: ',
        reply_markup=await SimpleCalendar(locale='').start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    calendar = SimpleCalendar(
        locale='', show_alerts=True
    )
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2027, 12, 31))
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        value = await cache.get(f'{callback.from_user.id}_course')
        if value is not None:
            course = loads(value)
            courseScheduleIn = CourseScheduleIn(courseUid=course.get('uid'), startDate=date)
            await CourseScheduleMng().create(courseScheduleIn)
            await callback.message.answer(f'Ви вибрали {date.strftime("%d/%m/%Y")}')
            await setCourse(message=callback.message, state=state)
