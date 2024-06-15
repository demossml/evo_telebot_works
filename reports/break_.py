from arrow import utcnow, get
from bd.model import (
    Session,
    Shift_Opening_Report,
)
from .inputs import AfsInput

from pprint import pprint

import logging
import sys


logger = logging.getLogger(__name__)

# Определение переменных с именем, описанием и MIME-типом
name = "🕒️🚬🌯перерыв ➡️".upper()
desc = "Собирает данные о перерывах"
mime = "text"


# Функция для получения входных данных сеанса
def get_inputs(session: Session):
    return {
        "location": AfsInput,
    }


# Функция для генерации данных
def generate(session: Session):
    result = []
    logger.info("Starting to generate break report")

    try:

        params = session.params["inputs"]["0"]  # Извлечение параметров из сеанса
        logger.info("Parameters extracted: %s", params)

        since = (
            utcnow().replace(hour=3, minute=00).isoformat()
        )  # Установка времени начала суток (3:00 UTC)
        until = (
            utcnow().replace(hour=20, minute=59).isoformat()
        )  # Установка времени конца суток (20:59 UTC)

        # Поиск первого документа открытия смены для текущего пользователя
        documents_open = (
            Shift_Opening_Report.objects(
                __raw__={
                    "openData": {"$gte": since, "$lt": until},
                    "x_type": "OPEN",
                    "user_id": session.user_id,
                }
            )
            .order_by("-openData")
            .first()
        )
        logger.info("Shift opening document found: %s", documents_open)

        # Поиск первого документа перерыва для текущего пользователя и магазина, где открыта смена
        documents_break = (
            Shift_Opening_Report.objects(
                __raw__={
                    "openData": {"$gte": since, "$lt": until},
                    "x_type": "BREAK",
                    "break": "open",
                    "shop_id": documents_open.shop,
                }
            )
            .order_by("-openData")
            .first()
        )
        logger.info("Break document found: %s", documents_break)

        # Обработка данных о перерыве, если такие данные найдены
        if documents_break:
            delta = (
                (
                    get(params["location"]["data"]) - get(documents_break.openData)
                ).seconds
                // 60
                % 60
            )
            logger.info("Break duration calculated: %d minutes", delta)

            if delta > 0:
                result_delta = f"{delta} минут."
            else:
                result_delta = "Меньше минуты".upper()
            break_data = {
                "user_id": session.user_id,
                "closeDate": params["location"]["data"],
                "openData": documents_break.openData,
                "break": "closed",
                "x_type": "BREAK",
                "shop_id": documents_open.shop,
                "close_location": params["location"],
                "delta": delta,
            }

            # Добавление результатов в список result
            result.append(
                {
                    "перерыв закончился".upper(): break_data["closeDate"][:16],
                    "Время перерыва:".upper(): result_delta,
                }
            )
            logger.info("Break data processed and added to results")

        else:
            # Обработка данных, если перерыв еще не начат
            break_data = {
                "user_id": session.user_id,
                "openData": params["location"]["data"],
                "x_type": "BREAK",
                "break": "open",
                "shop_id": documents_open.shop,
                "open_location": params["location"],
            }
            # Добавление результатов в список result
            result.append({"перерыв начался".upper(): break_data["openData"][:16]})
            logger.info("Break start data processed and added to results")

        # Обновление данных о перерыве в базе данных
        Shift_Opening_Report.objects(
            user_id=session.user_id,
            openData=break_data["openData"],
        ).update(**break_data, upsert=True)
        logger.info("Break data updated in the database: %s", break_data)

        return result
    except Exception as e:
        logger.error("Ошибка: %s на строке %s", e, sys.exc_info()[-1].tb_lineno)
        return result
