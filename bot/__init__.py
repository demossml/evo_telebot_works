import logging
from telegram import Telegram
from config import TELEGRAM_TOKEN_2
from bd.model import get_session, create_massage, find_employee
from state_machine import handle_message
from util_s import format_message_list4, send_scheduled_message

# Основной логгер
logger = logging.getLogger(__name__)


async def handler(params, bot):
    try:
        logger.info("Начало обработки сообщения")

        # Создание сообщения
        message = create_massage(params)
        logger.info(f"Созданное сообщение: {message}")

        # Получение сессии пользователя
        session = get_session(message.user_id)
        logger.debug(f"Полученная сессия: {session}")

        session.message = message
        session.employee = find_employee(session.user_id)

        # Обработка сообщения
        await handle_message(bot, message, session)
        logger.info(f"Сообщение успешно обработано {session.user_id}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Запуск бота")

    try:
        # Инициализация бота
        bot = Telegram(TELEGRAM_TOKEN_2, handler)

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
