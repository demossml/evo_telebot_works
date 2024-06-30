from telegram import Telegram
from config import TELEGRAM_TOKEN_2
from bd.model import get_session, create_massage, find_employee
from state_machine import handle_message, send_daily_welcome_message

import logging

logger = logging.getLogger(__name__)


async def handler(params, bot):
    try:
        logger.info(f"Beginning of message processing ")

        # Создание сообщения
        message = create_massage(params)
        logger.info(f"Созданное сообщение: {message}")

        # Получение сессии пользователя
        session = get_session(message.user_id)
        logger.debug(f"Session received: {session}")

        session.message = message
        session.employee = find_employee(session.user_id)

        # Обработка сообщения
        await handle_message(bot, message, session)
        await send_daily_welcome_message(bot)
        logger.info(f" Message processed successfully {session.user_id}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Launching the bot")
    try:
        bot = Telegram(TELEGRAM_TOKEN_2, handler)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
