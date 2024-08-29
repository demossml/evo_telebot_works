import telebot
from telebot import types
import schedule
from datetime import datetime
import pytz
import time
from check_store_opening import (
    format_message_list4,
    send_scheduled_message,
    get_electro_sales_plan,
)
from bd.model import Сonsent, Chat
from get_questionnaire import generate_text_message
import threading
import logging
import sys


logger = logging.getLogger(__name__)
# Токен вашего бота, который вы получили от BotFather
TOKEN = "5758434493:AAFNF4dj8w45SXReZRVxWzj5PH7L6vfnSqI"

# ID чата (группы), куда будут отправляться сообщения
CHAT_ID = -1002170989908
CHAT_ID_2 = -1002162641204

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)


# Функции для отправки сообщений по расписанию
def send_message():
    messages = format_message_list4(send_scheduled_message())
    for m in messages:
        bot.send_message(CHAT_ID, m, parse_mode="MarkdownV2")


# Функции для отправки сообщений по расписанию
def send_message2():
    result = get_electro_sales_plan()

    image_bytes = result[1]
    # print(image_bytes)

    # # Отправка изображения как фото
    try:
        bot.send_photo(CHAT_ID_2, photo=image_bytes)
        logger.info(f"Photo sent successfully to chat_id {CHAT_ID_2}")
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

    if len(result) > 0:
        # Отправляем сообщения
        messages = format_message_list4(result[0])
        try:
            for m in messages:
                bot.send_message(CHAT_ID_2, m, parse_mode="MarkdownV2")
            logger.info(f"Messages sent successfully to chat_id {CHAT_ID_2}")
        except Exception as e:
            logger.exception(f"Error sending messages to chat_id {CHAT_ID_2}")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


def get_consent():
    try:
        logging.info("Fetching active consents")
        consent = Сonsent.objects(status="activ")

        if len(consent) > 0:
            logging.info(f"Found {len(consent)} active consents")

            for item in consent:
                user_id = item["user_id"]
                logging.info(f"Generating text message for user_id: {user_id}")

                message = generate_text_message(user_id)
                bot.send_message(CHAT_ID, message)

                params = {"status": "sent"}
                logging.info(
                    f"Updating consent status to 'sent' for user_id: {user_id}"
                )

                Сonsent.objects(user_id=user_id).update(**params, upsert=True)

        else:
            logging.info("No active consents found")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


# Устанавливаем временную зону MSK
msk = pytz.timezone("Europe/Moscow")


# Функция для планирования с учетом MSK
def schedule_msk_time(hour, minute, job_func):
    def msk_job():
        now = datetime.now(msk)
        if now.hour == hour and now.minute == minute:
            job_func()

    schedule.every().minute.do(msk_job)


@bot.message_handler(content_types=["new_chat_members"])
def on_user_joined(message: types.Message):
    logger.info(message)
    logger.info("New chat member joined: %s", message.new_chat_members)
    params = {
        "chat_id": message.chat.id,
        "chat_title": message.chat.title,
        "user_id": message.from_user.id,
        "status_type": "active",
        "TZ": None,
    }
    try:
        Chat.objects(chat_id=message.chat.id).update(**params, upsert=True)
        logger.info("User %s added to chat %s", message.from_user.id, message.chat.id)

    except Exception as e:
        logger.error("Error updating chat database: %s", str(e))


# Расписание сообщений по времени МСК
schedule_msk_time(8, 0, send_message)
schedule_msk_time(9, 10, send_message)
schedule_msk_time(14, 0, send_message2)
schedule_msk_time(18, 0, send_message2)
schedule_msk_time(20, 0, send_message2)
schedule_msk_time(10, 15, get_consent)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Настройка уровня логирования

    # Запуск планировщика в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Запуск бота
    bot.infinity_polling()
