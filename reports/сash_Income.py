# Получить продажи  по всем магазинам  в ₽.
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id,  id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from arrow import utcnow
from bd.model import Session, CashRegister
from pprint import pprint

name = "💸📥 Внесение ➡️".upper()
desc = "Внесение"
mime = "text"


class whoInput:
    desc = "Напишите от кого".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        return (
            {"id": "Р/С", "name": "Р/С ➡️".upper()},
            {"id": "Bagrationa", "name": "Bagrationa ➡️".upper()},
            {"id": "Skala", "name": "Skala ➡️".upper()},
            {"id": "Another", "name": "Another ➡️".upper()},
        )


class baseInput:
    desc = "Основание:"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "Инкассация", "name": "Инкассация ➡️".upper()},
            {"id": "Прочие", "name": "Прочие ➡️".upper()},
            {"id": "Услуги", "name": "Услуги ➡️".upper()},
            {"id": "Инвестиции", "name": "Инвестиции ➡️".upper()},
        )

        return output


class commentInput:
    desc = "Напишите основание ✍️".upper()
    type = "MESSAGE"


class CashIncomeInput:
    desc = "Напишите сумму ✍️".upper()
    type = "MESSAGE"


def get_inputs(session: Session):
    return {
        "who": whoInput,
        "base": baseInput,
        "comment": commentInput,
        "cashIncome": CashIncomeInput,
    }


def generate(session: Session):
    _dict = {}
    params = session.params["inputs"]["0"]
    pprint(params)
    _dict["user_id"] = session["user_id"]
    _dict["who"] = params["who"]
    _dict["comment"] = params["comment"]
    _dict["cash"] = int(params["cashIncome"])
    _dict["base"] = params["base"]
    _dict["x_type"] = "CASH_INCOME"
    _dict["closeDate"] = utcnow().now().isoformat()
    number = CashRegister.objects().order_by("-closeDate").first()
    if number:
        number_ = number["number"] + 1
    else:
        number_ = 1

    _dict["number"] = number_
    _dict["payment"] = "cash"
    pprint(_dict)

    CashRegister.objects(closeDate=_dict["closeDate"]).update(**_dict, upsert=True)
    result = {
        "От:": params["who"],
        "Коментарий:": params["comment"],
        "Сумма:": int(params["cashIncome"]),
        "Основание:": params["base"],
        "Тип:": "Внесение:",
        "Дата:": utcnow().now().isoformat()[0:16],
        "№:": number_,
    }

    return [result]
