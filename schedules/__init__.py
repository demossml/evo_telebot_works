import telebot
import schedule
from datetime import datetime
import pytz
import time
from check_store_opening import (
    format_message_list4,
    send_scheduled_message,
    get_electro_sales_plan,
)
from bd.model import Сonsent
from get_questionnaire import generate_text_message
import logging
import sys


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot_1.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
# Токен вашего бота, который вы получили от BotFather
TOKEN = "5758434493:AAFNF4dj8w45SXReZRVxWzj5PH7L6vfnSqI"

# ID чата (группы), куда будут отправляться сообщения
CHAT_ID = -1001157232415
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


# Устанавливаем временную зону MSK
msk = pytz.timezone("Europe/Moscow")


# Function for scheduling with MSK timezone
def schedule_msk_time(hour, minute, job_func):
    def msk_job():
        now = datetime.now(msk)
        if now.hour == hour and now.minute == minute:
            logging.info(f"Executing scheduled job at {hour:02d}:{minute:02d} MSK")
            job_func()

    logging.info(f"Scheduling job at {hour:02d}:{minute:02d} MSK every day")
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(msk_job)


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


# Расписание сообщений по времени МСК
schedule_msk_time(8, 0, send_message)
schedule_msk_time(9, 10, send_message)
schedule_msk_time(14, 0, send_message2)
schedule_msk_time(18, 0, send_message2)
schedule_msk_time(20, 0, send_message2)
schedule_msk_time(19, 50, get_consent)


# Main loop
try:
    logging.info("Starting the scheduler main loop")
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Scheduler stopped by user")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
