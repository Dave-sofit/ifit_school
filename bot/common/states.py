from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    waitingContact = State()


class ControlState(StatesGroup):
    waitingControlObjectType = State()
    waitingControlObject = State()
    waitingAttribute = State()
    waitingDescriptions = State()


class EditingState(StatesGroup):
    waitingData = State()


class InformingState(StatesGroup):
    waitingProduct = State()
    waitingAction = State()
    waitingPlace = State()
    waitingDetails = State()
