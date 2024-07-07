from bd.model import Session, Сonsent

import sys
import logging

logger = logging.getLogger(__name__)

name = "💰 Желаемый уровень заработной платы ➡️".upper()
desc = "Желаемый уровень заработной платы"
mime = "text"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    try:
        room = session["room"]

        report_data = {"user_id": session.user_id, "relatives_information": []}

        result = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            params = session.params["inputs"][str(i)]
            # Получение параметров из сессии
            report_data["relatives_information"].append(params)

            result.append(
                {
                    "Ф.И.О.": params.get("close_relati", "Нет данных"),
                    "Дата рождения": params.get("full_name", "Нет данных"),
                    "Гражданство": params.get("citizenship", "Нет данных"),
                    "Место рождения": params.get("place_of_birth", "Нет данных"),
                    "Данные внесены в Вашу анкету": "📝",
                }
            )

        Сonsent.objects(user_id=session.user_id).update(**report_data, upsert=True)

        return result
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
