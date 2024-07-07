from bd.model import Session, Сonsent


from .inputs import (
    СompanyAddressInput,
    ReasonForLeavingInput,
    PositionInput,
    WorkStartDateInput,
    WorkEndDateInput,
    DocStatusInput,
)
import sys
import logging

logger = logging.getLogger(__name__)

name = "💼  Трудовая деятельность ➡️".upper()
desc = "Трудовая деятельность"
mime = "text"


def get_inputs(session: Session):

    try:
        room = session["room"]

        return {
            "company": СompanyAddressInput,
            "position": PositionInput,
            "work_start_date": WorkStartDateInput,
            "work_end_date": WorkEndDateInput,
            "reason_forLeaving": ReasonForLeavingInput,
            "docStatus": DocStatusInput,
        }

    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


def generate(session: Session):
    try:
        room = session["room"]

        report_data = {"user_id": session.user_id, "works_information": []}

        result = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            params = session.params["inputs"][str(i)]
            # Получение параметров из сессии
            report_data["works_information"].append(params)

            result.append(
                {
                    "Организация:": params.get("company", "Нет данных"),
                    "Должность:": params.get("position", "Нет данных"),
                    "Дата поступления:": params.get("work_start_date", "Нет данных"),
                    "Дата увольнения:": params.get("work_end_date", "Нет данных"),
                    "Причина увольнения:": params.get(
                        "reason_forLeaving", "Нет данных"
                    ),
                    "Данные внесены в Вашу анкету:": "📝",
                }
            )

        Сonsent.objects(user_id=session.user_id).update(**report_data, upsert=True)

        return result
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
