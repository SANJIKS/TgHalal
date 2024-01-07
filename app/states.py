from aiogram.fsm.state import StatesGroup, State

class CompositionState(StatesGroup):
    checking = State()
    finish = State()

class SendCheck(StatesGroup):
    what_tariff = State()
    waiting_for_check = State()
    finish = State()