from bd.model import Session, Сonsent
from .inputs import (
    EducationInput,
    EducationStartDateInput,
    EducationEndDateInput,
    DocStatusInput,
    SpecializationInput,
    EducationInstitutionNameInput,
)

import sys
import logging

logger = logging.getLogger(__name__)

name = "🎓  образование ➡️".upper()
desc = "Образование"
mime = "text"


def get_inputs(session: Session):
    return {
        "education": EducationInput,
        "education_institution_name": EducationInstitutionNameInput,
        "education_start_date": EducationStartDateInput,
        "education_end_date": EducationEndDateInput,
        "specialization": SpecializationInput,
        "docStatus": DocStatusInput,
    }


def generate(session: Session):
    try:
        room = session["room"]

        report_data = {"user_id": session.user_id, "education": []}

        result = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            params = session.params["inputs"][str(i)]
            # Получение параметров из сессии
            report_data["education"].append(params)

            result.append(
                {
                    "Образование:": params.get("education", "Нет данных"),
                    "Название учебного заведения:": params.get(
                        "education_institution_name", "Нет данных"
                    ),
                    "Дата поступления": params.get(
                        "education_start_date", "Нет данных"
                    ),
                    "Дата окончания": params.get("education_end_date", "Нет данных"),
                    "Специализация": params.get("specialization", "Нет данных"),
                    "Данные внесены в Вашу анкету": "📝",
                }
            )

        Сonsent.objects(user_id=session.user_id).update(**report_data, upsert=True)

        return result
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
