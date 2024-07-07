from bd.model import Session, Сonsent


from .inputs import (
    SkillsInput,
    AdvantagesInput,
    HobbiesInput,
    AdditionalInformationInput,
    DesiredSalaryInput,
)
import sys
import logging

logger = logging.getLogger(__name__)

name = "📋 Доп. информация ➡️".upper()
desc = "Трудовая деятельность"
mime = "text"


def get_inputs(session: Session):

    try:

        return {
            "skills": SkillsInput,
            "advantages": AdvantagesInput,
            "hobbies": HobbiesInput,
            # "additionalInformation": AdditionalInformationInput,
            "desiredSalary": DesiredSalaryInput,
        }

    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


def generate(session: Session):

    try:
        # Получение параметров из сессии
        params = session.params["inputs"]["0"]
        params.update({"user_id": session.user_id})

        Сonsent.objects(user_id=session.user_id).update(**params, upsert=True)

        result = {
            "Навыки:": params["skills"],
            "Преимущества:": params["advantages"],
            "Хобби:": params["hobbies"],
            "ЗП:": params["desiredSalary"],
            "Данные внесены в Вашу анкету": "📝",
        }
        logging.info(result)

        return [result]
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
