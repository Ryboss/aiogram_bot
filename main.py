import logging
import requests
import json
import os
import csv

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from app.core.config import BOT_TOKEN, RANDOM_IMAGE_API, USER_CREATE_URL, BASE_URL, GET_USERS_URL
from app.endpoints import users
from app.core.utils import generate_excel, generate_json_to_excel

# Приложение FastApi
app = FastAPI(title="BOT")


# Логирование
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
app.include_router(users.router)


# Подключаемся к боту по ТОКЕНУ
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Команды распознаваемые ботом
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    await message.reply("Привет!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['help'])
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
        "phone": str(message["contact"].phone_number)
        }
        try:
            await ac.post(USER_CREATE_URL, json=payload)
            await message.answer('Вы зарегистровались!', reply_markup=types.ReplyKeyboardRemove())
        except IntegrityError as e:
            await message.answer("Такой пользователь уже существует!", reply_markup=types.ReplyKeyboardRemove())
            log.info(e.args[0])


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
        users = await ac.get(GET_USERS_URL)
        print(users.text)
        await message.answer(users.text)


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


# Запускаем бота через FastApi
@app.on_event("startup")
async def startup() -> None:
    await dp.start_polling()


@app.on_event("shutdown")
async def shutdown() -> None:
    pass
