from typing import Callable
from enum import Enum
import telebot
from telebot import types
from arrow import utcnow
import io
import sys
import mimetypes
import asyncio
import time


import os


# Импорт моделей и функций из других модулей
from bd.model import Message, Session, GetTime, Employees, Shop, Schedules
from reports import reports, get_reports
from util_s import (
    format_message_list4,
    xls_to_json_format_change,
    send_scheduled_message,
    welcome_message,
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


# Функция для отправки приветственного сообщения
async def send_daily_welcome_message(bot: telebot.TeleBot):
    logger.info("start send_daily_welcome_message")

    try:
        messages = format_message_list4(send_scheduled_message())
        for m in messages:
            await bot.send_message(5700958253, m, parse_mode="MarkdownV2")

    except Exception as e:
        logger.exception("Error handling message")
        logger.error(f" Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


# Определить состояния сессии
class State(str, Enum):
    INIT = "INIT"  # Начальное состояние сеанса
    MENU = "MENU"  # Меню с выбором отчета
    INPUT = "INPUT"  # Ввод данных для отчета
    REPLY = "REPLY"  # Ответ на вопросы отчета
    READY = "READY"  # Готовность отчета к отправке


# Обработчик входящие сообщения
async def handle_message(bot: telebot.TeleBot, message: Message, session: Session):
    # Определить список стартовых команд
    start_ = ("/start",)
    # Определить список стартовых команд
    start = ("Menu", "/start", "Меню")

    if str(message.chat_id) == "-1001157232415":
        logger.info(message)
    else:
        # Проверьте, является ли сообщение командой запуска.
        if message.text in start_:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn_address = types.KeyboardButton("Меню")
            markup.add(btn_address)
            await bot.send_message(
                message.chat_id,
                welcome_message,
                reply_markup=markup,
            )

        # Проверьте, является ли сообщение командой запуска.
        if message.text in start:
            # Сброс состояния сессии и комнаты
            session.state = State.INIT
            session.room = "0"
            session.update(room=session.room, state=session.state)
        if message.text == "/log":
            text_file_path = "bot.log"
            with open(text_file_path, "rb") as text_file:
                await bot.send_document(message.chat_id, document=text_file)
        # Проверяем, нужно ли отправлять приветственное сообщение
        # await send_daily_welcome_message(bot)
        # Определим функцию для следующего шага
        next = lambda: handle_message(bot, message, session)
        try:
            # Вызов соответствующего обработчика состояния на основе состояния сессии
            logger.info(f"{session.state} {message.chat_id}")
            await states[session.state](bot, message, session, next)
        except Exception as e:
            # print(e)
            # raise ex
            logger.exception("Error handling message")
            logger.error(
                f"{ message.chat_id}, Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
            )
            # Обработка исключений и уведомление пользователя
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn_address = types.KeyboardButton("Меню")
            markup.add(btn_address)
            await bot.send_message(
                message.chat_id,
                f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}",
                reply_markup=markup,
            )
            session.state = State.INIT
            next()


# Обработка состояния INIT (начальное состояние)
async def handle_init_state(
    bot: telebot.TeleBot, message: Message, session: Session, next: Callable
):
    try:
        # Создайте меню «Пуск» с опциями отчета
        start_menu = types.InlineKeyboardMarkup(row_width=2)
        for name, report in get_reports(session).items():
            # print(name)
            button = types.InlineKeyboardButton(report.name, callback_data=name)
            start_menu.add(button)
        # Отправьте приветственное сообщение через меню «Пуск»
        await bot.send_message(message.chat_id, "Привет", reply_markup=start_menu)
        logger.info(f"Sent start menu to chat {message.chat_id}")

        # Инициализируем параметры сессии
        room = session.room
        session.params = {"inputs": {room: {}}}
        # Переход в состояние МЕНЮ
        session.state = State.MENU

        # Обновляем состояние сессии и params
        session.update(params=session.params, state=session.state)
        logger.info(f"Handled init state for chat {message.chat_id}")
    except Exception as e:
        logger.exception("Error sending messages")
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


# Обработка состояния MENU (состояние выбора опции в меню)
async def handle_menu_state(
    bot: telebot.TeleBot, message: Message, session: Session, next: Callable
):
    try:
        # Установить выбранный отчет в параметрах сессии
        session.params["report"] = message.text

        # Переход в состояние INPUT
        session.state = State.INPUT

        # Обновляем состояние сессии
        session.update(state=session.state, params=session.params)
        logger.info(f"Handled menu state for chat {message.chat_id}")

        await next()
    except Exception as e:
        logger.exception("Error sending messages")
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


# Обработка состояния INPUT(Ввод данных для отчета)
async def handle_input_state(bot, message, session, next):
    try:
        report = reports[session.params["report"]]
        # Перебираем поля ввода отчета
        for name, Input in report.get_inputs(session).items():
            # print(name)
            room = session.room
            if name not in session.params["inputs"][room]:
                session.params["input"] = name
                session.update(params=session.params)
                input = Input()
                # Обработка различных типов ввода
                if input.type == "SELECT":
                    # Создаем кнопку для каждой опции
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    options = input.get_options(session)  # [{}, {}, {}, ...]
                    for option in options:  # [({}, 0), ({}, 1), ({}, 2)]
                        button = types.InlineKeyboardButton(
                            option["name"], callback_data=option["id"]
                        )
                        markup.add(button)
                if input.type == "LOCATION":
                    # Обработка ввода LOCATION (местоположения)
                    options = input.get_options(session)  # [{}, {}, {}, ...]
                    print(options[0]["name"])
                    markup = types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2
                    )
                    btn_address = types.KeyboardButton(
                        options[0]["name"], request_location=True
                    )
                    markup.add(btn_address)
                if input.type == "PHOTO":
                    # Обработка ввода фотографии
                    markup = types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2
                    )
                    btn_address = types.KeyboardButton("Меню")
                    markup.add(btn_address)
                    try:
                        await bot.send_message(
                            message.chat_id, input.desc, reply_markup=markup
                        )
                        logger.info(
                            f"Sent photo input message to chat {message.chat_id}"
                        )
                    except Exception as e:
                        logger.exception("Error sending photo input message")
                        logger.error(
                            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
                        )
                if input.type == "FILE":
                    # Обработка ввода файла
                    markup = types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2
                    )
                    btn_address = types.KeyboardButton("Меню")
                    markup.add(btn_address)
                    try:
                        await bot.send_message(
                            message.chat_id, input.desc, reply_markup=markup
                        )
                        logger.info(
                            f"Sent file input message to chat {message.chat_id}"
                        )
                    except Exception as e:
                        logger.exception("Error sending file input message")
                        logger.error(
                            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
                        )
                if input.type == "MESSAGE":
                    # Удаляем предыдущее сообщение и отправляем новое сообщение с клавиатурой
                    try:
                        await bot.delete_message(message.chat_id, message.message_id)
                        await bot.send_message(message.chat_id, input.desc)
                        logger.info(f"Sent message input to chat {message.chat_id}")
                    except Exception as e:
                        logger.exception("Error sending message input")
                        logger.error(
                            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
                        )
                if input.type == "SELECT":
                    # Удаляем предыдущее сообщение и отправляем новое сообщение с клавиатурой
                    try:
                        await bot.delete_message(message.chat_id, message.message_id)
                        await bot.send_message(
                            message.chat_id, input.desc, reply_markup=markup
                        )
                        logger.info(f"Sent select input to chat {message.chat_id}")
                    except Exception as e:
                        logger.exception("Error sending select input")
                        logger.error(
                            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
                        )
                if input.type == "LOCATION":
                    # Удаляем предыдущее сообщение и отправляем новое сообщение с клавиатурой
                    try:
                        await bot.delete_message(message.chat_id, message.message_id)
                        await bot.send_message(
                            message.chat_id, input.desc, reply_markup=markup
                        )
                        logger.info(f"Sent location input to chat {message.chat_id}")
                    except Exception as e:
                        logger.exception("Error sending location input")
                        logger.error(
                            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
                        )
                session.state = State.REPLY
                session.update(state=session.state)
                # session.save()

                logger.info(f"Handled input state for chat {message.chat_id}")

                return
        # Переход в состояние READY (Обработка готовности отчета)
        session.state = State.READY

        # Обновляем состояние сессии
        session.update(state=session.state)
        # logger.info(f"Handled init state for chat {message.chat_id}")
        await next()
    except Exception as e:
        logger.exception("Error handling input state")
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


# Обработка состояния REPLY


async def handle_reply_state(bot, message, session, next):
    try:
        input_name = session.params["input"]
        room = session.room
        logger.info(f"Initialized input_name and room for chat {session.user_id}")
    except Exception as e:
        logger.exception(
            f"Error initializing input_name and room for chat {message.chat_id}"
        )
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {message.chat_id}"
        )

    try:
        # Обработка команды "open" для перехода в следующую комнату
        if message.text == "open":
            session.room = str(int(session.room) + 1)
            session.params["inputs"][session.room] = {}
            session.update(params=session.params, room=session.room)
            logger.info(
                f"Handled 'open' command for chat {session.user_id}, moved to room {session.room}"
            )
    except Exception as e:
        logger.exception(f"Error handling 'open' command for chat {session.user_id}")
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {session.user_id}"
        )

    try:
        # Создайте новое поле ввода в текущей комнате, если оно не существует
        if str(room) not in session.params["inputs"]:
            session.params["inputs"][str(room)] = {}
            session.update(params=session.params)
            logger.info(
                f"Created new input field for room {room} in chat {session.user_id}"
            )
    except Exception as e:
        logger.exception(f"Error creating new input field for chat {session.user_id}")
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {session.user_id}"
        )

    try:
        # Сохраняйте введенные пользователем данные в зависимости от типа сообщения
        session.params["inputs"][str(room)][input_name] = message.text
        session.update(params=session.params)
        logger.info(f"Saved user input for room {room} in chat {session.user_id}")
    except Exception as e:
        logger.exception(f"Error saving user input for chat {session.user_id}")
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {session.user_id}"
        )

    try:
        # Обработка локации
        if message.location:
            session.params["inputs"][str(room)][input_name] = (
                utcnow().now().to("Etc/GMT-3").isoformat()
            )
            session.params["inputs"][str(room)][input_name] = {}
            session.params["inputs"][str(room)][input_name]["data"] = (
                utcnow().now().to("Etc/GMT-3").isoformat()
            )
            session.params["inputs"][str(room)][input_name][
                "lat"
            ] = message.location.latitude
            session.params["inputs"][str(room)][input_name][
                "lon"
            ] = message.location.longitude
            session.update(params=session.params)

            _dict2 = {}
            if "shop" in session.params["inputs"]["0"]:
                uuid = session.params["inputs"]["0"]["shop"]
                doc = [i.uuid for i in Shop.objects(uuid=uuid)]
                for i in Employees.objects(lastName=str(session["user_id"])):
                    _dict2.update(
                        {
                            "shopUuid": doc[0],
                            "employees": i["name"],
                            "openingData": utcnow().now().to("Etc/GMT-3").isoformat(),
                        }
                    )
                GetTime.objects(user_id=session.user_id).update(**_dict2, upsert=True)
            logger.info(f"Handled location data for chat {session.user_id}")
    except Exception as e:
        logger.exception(f"Error handling location for chat {session.user_id}")
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {session.user_id}"
        )

    try:
        # Обработка фото
        if message.photo:
            session.params["inputs"][str(room)][input_name] = {}
            session.params["inputs"][str(room)][input_name]["photo"] = message.photo[
                -1
            ].file_id
            session.update(params=session.params)
            logger.info(f"Handled photo data for chat {session.user_id}")
    except Exception as e:
        logger.exception(f"Error handling photo for chat {session.user_id}")
        logger.error()

    try:
        # Обработка файла
        if message.document:
            mime_type = message.document.mime_type
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)

            logger.info(f"Handled document data for chat {session.user_id}")

            # Получаем имя файла
            file_name = os.path.basename(file_info.file_path)

            # Проверяем расширение файла
            file_extension = os.path.splitext(file_name)[1]
            print(file_extension)

            if not file_extension:
                file_extension = mimetypes.guess_extension(mime_type)
            print(file_extension)

            #  Проверяем тип MIME файла
            if file_extension in [".xls", ".xlsx"]:
                print("xls")

                src_list = xls_to_json_format_change(downloaded_file, file_extension)
                # logger.info(src_list)
            session.params["inputs"][str(room)][input_name] = src_list
            session.state = State.INPUT
            session.update(state=session.state)

    except Exception as e:
        logger.exception(f"Error handling document for chat {session.user_id}")
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {session.user_id}"
        )

    try:
        # Переход в состояние INPUT (Обработка ввода данных)
        session.state = State.INPUT
        session.update(state=session.state)
        logger.info(f"Updated session state to INPUT for chat {session.user_id}")
    except Exception as e:
        logger.exception(
            f"Error updating session state to INPUT for chat {session.user_id}"
        )
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {session.user_id}"
        )

    try:
        logger.info(f"Handled init state for chat {session.user_id}")
        await next()
        logger.info(f"Executed next handler for chat {session.user_id}")
    except Exception as e:
        logger.exception(f"Error executing next handler for chat {session.user_id}")
        logger.error(
            f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno} для chat {session.user_id}"
        )


# Обработка состояния READY
async def handle_ready_state(bot, message, session, next):
    # Получаем выбранный отчет из сессии
    report = reports[session.params["report"]]

    # Генерируем результат на основе выбранного отчета
    result = report.generate(session)

    print(report.mime)

    # Если тип отчета - изображение
    if report.mime == "image":
        # Если есть файлы изображений, отправляем их
        if len(result[0]) > 0:
            for k, v in result[0].items():
                file_id = v
                try:
                    await bot.send_photo(message.chat_id, file_id)
                    logger.info(f"Photo sent successfully to chat_id {message.chat_id}")
                except Exception as e:
                    logger.exception(
                        f"Error sending photo to chat_id {message.chat_id}"
                    )
                    logger.error(
                        f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
                    )

            # Форматируем и отправляем сообщения из списка результатов
            messages = format_message_list4(result[1])
            try:
                for m in messages:
                    await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                logger.info(f"Messages sent successfully to chat_id {message.chat_id}")
            except Exception as e:
                logger.exception(f"Error sending messages to chat_id {message.chat_id}")
                logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
        else:
            # Если нет файлов изображений, только отправляем сообщения
            messages = format_message_list4(result[1])
            try:
                for m in messages:
                    await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                logger.info(f"Messages sent successfully to chat_id {message.chat_id}")
            except Exception as e:
                logger.exception(f"Error sending messages to chat_id {message.chat_id}")
                logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
    elif report.mime == "image_bytes":
        # print(result)

        if result[1] is not None:
            # Получение изображения
            image_bytes = result[1]
            # print(image_bytes)

            # # Отправка изображения как фото
            try:
                await bot.send_photo(message.chat_id, photo=image_bytes)
                logger.info(f"Photo sent successfully to chat_id {message.chat_id}")
            except Exception as e:
                logger.exception(f"Error sending photo to chat_id {message.chat_id}")
                logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

            if len(result) > 0:
                # Отправляем сообщения
                messages = format_message_list4(result[0])
                try:
                    for m in messages:
                        await bot.send_message(
                            message.chat_id, m, parse_mode="MarkdownV2"
                        )
                    logger.info(
                        f"Messages sent successfully to chat_id {message.chat_id}"
                    )
                except Exception as e:
                    logger.exception(
                        f"Error sending messages to chat_id {message.chat_id}"
                    )
                    logger.error(
                        f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
                    )
        else:
            # Если нет файлов изображений, только отправляем сообщения
            messages = format_message_list4(result[0])
            try:
                for m in messages:
                    await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                logger.info(f"Messages sent successfully to chat_id {message.chat_id}")
            except Exception as e:
                logger.exception(f"Error sending messages to chat_id {message.chat_id}")
                logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

    elif report.mime == "file":

        try:
            book_number = 1
            for book in result[1]:
                book_name = "book_" + str(book_number) + ".xlsx"

                binary_book_he = io.BytesIO()
                book.save(binary_book_he)
                binary_book_he.seek(0)
                binary_book_he.name = (
                    book_name  # Устанавливаем имя файла в объекте BytesIO
                )
                await bot.send_document(message.chat_id, document=binary_book_he)
                book_number += 1

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")
    elif report.mime == "docx":

        try:
            # # print(result)
            # print(type(result))
            binary_book = io.BytesIO()
            result.save(binary_book)
            binary_book.seek(0)
            binary_book.name = (
                "anketa.docx"  # Устанавливаем имя файла в объекте BytesIO
            )
            await bot.send_document(message.chat_id, document=binary_book)

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

    else:
        print(result)
        # Если нет файлов изображений, только отправляем сообщения
        messages = format_message_list4(result)
        try:
            for m in messages:
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
            logger.info(f"Messages sent successfully to chat_id {message.chat_id}")
        except Exception as e:
            logger.exception(f"Error sending messages to chat_id {message.chat_id}")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

    # Переход в состояние INPUT (Обработка начального состояния)
    session.state = State.INIT

    # Создаем клавиатуру с кнопкой "Меню"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_address = types.KeyboardButton("Меню")
    markup.add(btn_address)

    # Удаляем сообщение о результате и отправляем приветственное сообщение с клавиатурой
    try:
        await bot.delete_message(message.chat_id, message.message_id)
        logger.info(f"Message deleted successfully from chat_id {message.chat_id}")
    except Exception as e:
        logger.exception(f"Error deleting message from chat_id {message.chat_id}")
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

    try:
        await bot.send_message(message.chat_id, "👇", reply_markup=markup)
        logger.info(f"Welcome message sent successfully to chat_id {message.chat_id}")
    except Exception as e:
        logger.exception(f"Error sending welcome message to chat_id {message.chat_id}")
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

    # Обновляем состояние сессии
    session.update(state=session.state)


states = {
    State.INIT: handle_init_state,  # Обработка начального состояния
    State.MENU: handle_menu_state,  # Обработка меню с выбором отчета
    State.INPUT: handle_input_state,  # Обработка ввода данных
    State.REPLY: handle_reply_state,  # Обработка ответов на вопросы
    State.READY: handle_ready_state,  # Обработка готовности отчета
}
