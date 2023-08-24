from bd.model import Session, Documents, Users
from evotor.evotor import Evotor
from .inputs import TokenEvotorInput

name = "🛠 Настройки ➡️".upper()
desc = ""
mime = 'text'


def get_inputs(session: Session):
    # user = Users.objects(user_id=session.user_id)
    return {
        "token": TokenEvotorInput,

    }


def generate(session: Session):
    ev = Evotor(session.params["inputs"]['0']["token"])
    response = ev.get_response()
    if response:
        params = {
            'token': session.params["inputs"]['0']["token"],
            'user_id': session.user_id
        }

        Users.objects(user_id=session.user_id).update(**params, upsert=True)
        return [
            {
                'Токен': 'Зарегистрирован',
                'Сенхронизция закончится через': '1 час'
            }
        ]
    else:
        return [
            {
                'Токен': 'Неверен'
            }
        ]



