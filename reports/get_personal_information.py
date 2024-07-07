from bd.model import Session, Сonsent


from .inputs import (
    FullNameInput,
    DateOfBirthInput,
    CitizenshipInput,
    PlaceOfBirthInput,
)

import sys
import logging

logger = logging.getLogger(__name__)

name = "📝 Личная информация ➡️".upper()
desc = "Личная информация"
mime = "text"


def get_inputs(session: Session):
    return {
        "full_name": FullNameInput,
        "dateOf_birth": DateOfBirthInput,
        "citizenship": CitizenshipInput,
        "place_of_birth": PlaceOfBirthInput,
    }


def generate(session: Session):
    try:
        # Получение параметров из сессии
        params = session.params["inputs"]["0"]
        params.update({"user_id": session.user_id})

        Сonsent.objects(user_id=session.user_id).update(**params, upsert=True)

        result = {
            "Ф.И.О.:": params["full_name"],
            "Дата рождения:": params["dateOf_birth"],
            "Гражданство:": params["citizenship"],
            "Место рождения:": params["place_of_birth"],
            "Данные внесены в Вашу анкету": "📝",
        }
        logging.info(result)

        return [result]
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
