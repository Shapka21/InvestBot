from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    Money_minvol = State()
    Money_maxsharp = State()
    Stock = State()