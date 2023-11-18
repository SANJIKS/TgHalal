from aiogram.fsm.state import StatesGroup, State

class CompositionState(StatesGroup):
    checking = State()
    finish = State()