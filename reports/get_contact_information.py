from bd.model import Session, Сonsent


from .inputs import (
    ResidenceAddressInput,
    RegistrationAddressInput,
    PhoneInput,
)

import logging

logger = logging.getLogger(__name__)

name = "📞 Контактная информация ➡️".upper()
desc = "Личная информация"
mime = "text"


def get_inputs(session: Session):
    return {
        "residence_address": ResidenceAddressInput,
        "home_phone": PhoneInput,
    }


def generate(session: Session):
    # Получение параметров из сессии
    params = session.params["inputs"]["0"]
    params.update({"user_id": session.user_id})

    Сonsent.objects(user_id=session.user_id).update(**params, upsert=True)

    result = {
        "Адрес (место жительства)": params["residence_address"],
        "Адрес (место прописки)": params["registration_address"],
        "Телефон": params["home_phone"],
        "Данные внесены в Вашу анкету": "📝",
    }

    return [result]
