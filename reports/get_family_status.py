from bd.model import Session, Сonsent


from .inputs import (
    FullNameInput,
    СounterpartyInput,
    RelativeWorkInput,
)

import sys
import logging

logger = logging.getLogger(__name__)

name = "👪 Семейное положение ➡️".upper()
desc = "Семейное положение"
mime = "text"


def get_inputs(session: Session):
    # Получаем входные данные из сессии
    inputs = session.params.get("inputs", {}).get("0", {})

    # Если входных данных нет, возвращаем ввод для отчета по продажам
    if not inputs:
        return {"counterparty": СounterpartyInput}

    counterparty = inputs.get("counterparty", None)

    if counterparty == "married":
        return {
            "full_name_married": FullNameInput,
            "relative_work_married": RelativeWorkInput,
        }
    else:
        return {}


def generate(session: Session):
    try:
        counterparty = {
            "single/unmarried": "Не женат/не замужем",
            "married": "Женат/замужем",
            "divorced/divorced": "Разведен/разведена",
            "widower/widow": "Вдовец/вдова",
        }

        # Получение параметров из сессии
        params = session.params["inputs"]["0"]
        params.update({"user_id": session.user_id})

        Сonsent.objects(user_id=session.user_id).update(**params, upsert=True)

        result = {"Семейное положение:": counterparty[params["counterparty"]]}

        if params["counterparty"] == "married":

            result.update(
                {
                    "Место работы, должность:": params["relative_work_married"],
                }
            )

        result.update(
            {
                "Данные внесены в Вашу анкету": "📝",
            }
        )

        return [result]
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
