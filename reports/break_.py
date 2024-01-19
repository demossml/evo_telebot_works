from arrow import utcnow, get
from bd.model import (
    Session,
    Shift_Opening_Report,
)
from .inputs import AfsInput

from pprint import pprint

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

    params = session.params["inputs"]["0"]  # Извлечение параметров из сеанса

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
                "locationData": {"$gte": since, "$lt": until},
                "x_type": "OPEN",
                "user_id": session.user_id,
            }
        )
        .order_by("-openData")
        .first()
    )

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

    # Обработка данных о перерыве, если такие данные найдены
    if documents_break:
        delta = (
            (get(params["location"]["data"]) - get(documents_break.openData)).seconds
            // 60
            % 60
        )
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

    # Обновление данных о перерыве в базе данных
    Shift_Opening_Report.objects(
        user_id=session.user_id,
        openData=break_data["openData"],
    ).update(**break_data, upsert=True)

    return result
