import telebot
import schedule
import time
from check_store_opening import (
    format_message_list4,
    send_scheduled_message,
    get_electro_sales_plan,
)

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


# Расписание сообщений
schedule.every().day.at("08:00").do(send_message)
schedule.every().day.at("09:10").do(send_message)
schedule.every().day.at("14:00").do(send_message2)
schedule.every().day.at("18:00").do(send_message2)
schedule.every().day.at("20:00").do(send_message2)


# schedule.every().day.at("18:00").do(send_message, "Время ужина!")
# Добавьте свои собственные расписания, как вам угодно

# Основной цикл программы
while True:
    schedule.run_pending()
    time.sleep(1)
