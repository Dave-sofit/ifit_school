from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    waitingContact = State()


class InformingState(StatesGroup):
    waitingProduct = State()
    waitingAction = State()
    waitingPlace = State()
    waitingDetails = State()
