import logging
import requests
import json
import os
import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from app.core.config import BOT_TOKEN, RANDOM_IMAGE_API, USER_CREATE_URL, BASE_URL, GET_USERS_URL, GET_COMPANIES
from app.endpoints import users, companies
from app.models.telegram_models import UserState, ReportsFilters
from app.core.utils import generate_excel


# Приложение FastApi
app = FastAPI(title="BOT")

# Логирование
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

app.include_router(users.router)
app.include_router(companies.router)


# Подключаемся к боту по ТОКЕНУ
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


# Команды распознаваемые ботом
@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message, state: FSMContext):
    await message.reply(f"Привет, {message.from_user.username}!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")


@dp.message_handler(commands=["registration"])
async def share_phone(message: types.Message, state: FSMContext) -> None:
    """
    Запрос на отправку телефона
    """

    catalogKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard_button = types.KeyboardButton(text='Отправить номер', request_contact=True, )  # type: ignore
    catalogKBoard.add(keyboard_button)

    await message.answer(text="Отправьте номер телефона", reply_markup=catalogKBoard)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def registration(message: types.Message) -> None:
    """
    Регистрация пользователя
    """

    catalogKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard_button = types.KeyboardButton(text='Регистрация', request_contact=True, )  # type: ignore
    catalogKBoard.add(keyboard_button)

    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        payload = {
        "user_id": message.from_user.id,
        "phone": str(message["contact"].phone_number),
        "username": str(message.from_user.username)
        }

        try:
            await ac.post(USER_CREATE_URL, json=payload)
            await message.answer('Вы зарегистровались!', reply_markup=types.ReplyKeyboardRemove())
        except IntegrityError as e:
            await message.answer("Такой пользователь уже существует!", reply_markup=types.ReplyKeyboardRemove())
            log.info(e.args[0])


@dp.message_handler(commands=["get_companies"])
async def get_companies(message: types.Message) -> None:
    """
    Получение компаний
    """

    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        try:
            payload ={
            "file_path": f"companies_excel/generate_excel_{message.from_user.id}_{message.message_id}.xlsx"
            }
            companies = await ac.post(GET_COMPANIES, params=payload)
            await message.answer_document(open(payload["file_path"], "rb"))
        except IntegrityError as e:
            await message.answer("Такой пользователь уже существует!", reply_markup=types.ReplyKeyboardRemove())
            log.info(e.args[0])


#? Получение отчета через FSMContext
@dp.message_handler(commands=['get_report'])
async def get_report(message: types.Message, state: FSMContext):
    """
    Команда для запроса отчета
    <Выбор даты начала>
    """

    await message.answer("Выберите дату начала: ", reply_markup=await SimpleCalendar().start_calendar())
    await ReportsFilters.date_start.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=ReportsFilters.date_start)
async def get_calandar_date_start(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    await state.update_data(date_start=date.strftime("%d/%m/%Y"))

    if selected:
        await callback_query.message.answer(f'Вы выбрали {date.strftime("%d/%m/%Y")}')

    await callback_query.message.answer("Выберите дату конца: ", reply_markup=await SimpleCalendar().start_calendar())
    await ReportsFilters.date_end.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=ReportsFilters.date_end)
async def get_calandar_date_end(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    await state.update_data(date_end=date.strftime("%d/%m/%Y"))

    if selected:
        await callback_query.message.answer(f'Вы выбрали {date.strftime("%d/%m/%Y")}')
        await callback_query.message.answer(f"Отлично! Теперь введите название вашей компании")
        await ReportsFilters.company.set()


@dp.message_handler(state=ReportsFilters.company)
async def get_date_start(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    data = await state.get_data()
    await message.answer(f"Дата начала: {data['date_start']}\n"
                         f"Дата конца: {data['date_end']}\n"
                         f"Компания: {data['company']}")

    await state.finish()


@dp.message_handler(commands=["get_image"])
async def get_image(message: types.Message) -> None:
    """
    Получение рандомной фотографии
    """

    image_url = json.loads(requests.get(RANDOM_IMAGE_API, stream=True).content)["file"]
    await message.answer_photo(photo=image_url)


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def save_files(message: types.Message) -> None:
    """
    Сохранение и обработка файлов
    """

    file_name = message["document"].file_name.split(".")
    file_type = file_name[len(file_name) - 1]
    file = await bot.get_file(file_id=message.document.file_id)
    file_path = file.file_path
    destination_dir = os.path.join("download_files", str(message.from_user.id))
    print(file_path)
    await bot.download_file(file_path=file_path, destination_dir=destination_dir, make_dirs=True)

    if file_type == "xlsx":
        await message.answer("Вы скинули файл Excel")

    elif file_type in ("docx", "doc"):
        await message.answer("Вы скинули файл Word")

    elif file_type == "csv":
        csv_path = os.path.join("download_files", str(message.from_user.id), file_path)
        path_to_save = await generate_excel(file_path=csv_path, message=message)

        await message.answer("Вы скинули файл CSV файл\nСгенерирована Excel")
        await message.answer_document(open(path_to_save, "rb"))


@dp.message_handler(commands=["get_users"])
async def get_users(message: types.Message) -> None:
    """
    Получение списка пользователей
    """

    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        payload ={
            "file_path": f"users_excel/generate_excel_{message.from_user.id}_{message.message_id}.xlsx"
        }
        await ac.post(GET_USERS_URL, params=payload)

        await message.answer_document(open(payload["file_path"], "rb"))


@dp.message_handler(commands=["get_id"])
async def get_my_id(message: types.Message) -> None:
    """
    Получение своего ID
    """

    await message.answer(f"Ваш ID в теграме: {message.from_user.id}")


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


# Запускаем бота через FastApi
@app.on_event("startup")
async def startup() -> None:
    asyncio.create_task(dp.start_polling())


@app.on_event("shutdown")
async def shutdown() -> None:
    pass
