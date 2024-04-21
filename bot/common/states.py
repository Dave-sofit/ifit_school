from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    waitingContact = State()


class ControlState(StatesGroup):
    waitingControlObjectType = State()
    waitingControlObject = State()
    waitingAttribute = State()
    waitingDescriptions = State()
    waitingContent = State()
    waitingCertificate = State()
    waitingPlace = State()
    waitingCourseAttribute = State()
    waitingCourseDescriptions = State()
    waitingCoursePrice = State()
    waitingCourseExam = State()
    waitingCourseLocation = State()
    waitingCourseDate = State()


class EditingState(StatesGroup):
    waitingData = State()


class InformingState(StatesGroup):
    waitingProduct = State()
    waitingAction = State()
    waitingPlace = State()
    waitingDetails = State()
