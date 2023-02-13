from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    name = State()
    address = State()


class ReportsFilters(StatesGroup):
    date_start = State()
    date_end = State()
    company = State()
