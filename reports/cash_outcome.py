from arrow import utcnow
from bd.model import Session, CashRegister
from pprint import pprint
from .util import period_to_date, get_intervals

name = "💸🔙 Выплата ➡️".upper()
desc = "Выплата"
mime = "text"


class PaymentFormatInput:
    name = "Выберите форму оплаты"
    desc = "Выберите форму оплаты"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "cash", "name": "Нал факт ➡️".upper()},
            {"id": "cashless_payments", "name": "Безналичный расчет ➡️".upper()},
        ]
        return output


class PeriodOpenDateInput:
    name = "Магазин"
    desc = "Выберите период 🗓".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "day", "name": "День ➡️".upper()},
            {"id": "week", "name": "Неделя ➡️".upper()},
            {"id": "fortnight", "name": "Две недели ➡️".upper()},
            {"id": "month", "name": "Месяц ➡️".upper()},
            {"id": "two months", "name": "Два месяца ➡️".upper()},
        ]

        return output


class OpenDateInput:
    desc = "Выберите дату начало пириода 📅".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session["params"]["inputs"]["0"]["periodOpenDate"])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({"id": left, "name": "{} ➡️".format(left[0:10])})

        return output


class whoInput:
    desc = "Напишите от кому ✍️".upper()
    type = "MESSAGE"


class baseInput:
    desc = "Основание ".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "Аренда1", "name": "Аренда1 ➡️".upper()},
            {"id": "ЗП", "name": "ЗП ➡️".upper()},
            {"id": "ЗП Д", "name": "ЗП Д ➡️".upper()},
            {"id": "Аренда", "name": "Аренда ➡️".upper()},
            {"id": "ГСМ", "name": "ГСМ ➡️".upper()},
            {"id": "Закупка Товара", "name": "Закупка Товара ➡️".upper()},
            {"id": "Прочие", "name": "Прочие ➡️".upper()},
        ]

        return output


class commentInput:
    desc = "Напишите коментырий ✍️".upper()
    type = "MESSAGE"


class CashOutcomeInput:
    desc = "Напишите сумму ✍️".upper()
    type = "MESSAGE"


def get_inputs(session: Session):
    if session.params["inputs"]["0"]:
        if session.params["inputs"]["0"]["payment"] == "cash":
            return {
                "who": whoInput,
                "base": baseInput,
                "comment": commentInput,
                "cashOutcome": CashOutcomeInput,
            }
        else:
            return {
                "periodOpenDate": PeriodOpenDateInput,
                "openDate": OpenDateInput,
                "who": whoInput,
                "base": baseInput,
                "comment": commentInput,
                "cashOutcome": CashOutcomeInput,
            }
    else:
        return {
            "payment": PaymentFormatInput,
        }


def generate(session: Session):
    params = session.params["inputs"]["0"]
    if session.params["inputs"]["0"]["payment"] == "cash":
        close_date = utcnow().now().isoformat()
    else:
        close_date = params["openDate"]

    _dict = {
        "user_id": session["user_id"],
        "payment": params["payment"],
        "who": params["who"],
        "base": params["base"],
        "comment": params["comment"],
        "cash": float(params["cashOutcome"]),
        "x_type": "CASH_OUTCOME",
        "closeDate": close_date,
    }

    number = CashRegister.objects().order_by("-closeDate").first()
    _dict["number"] = number["number"] + 1

    CashRegister.objects(closeDate=_dict["closeDate"]).update(**_dict, upsert=True)

    if params["payment"] == "cashless_payments":
        payment = "Безналичный расчет"
    else:
        payment = "Наличный расчет"

    result = {
        "Кому:": params["who"],
        "Основание:": params["base"],
        "Сумма:": float(params["cashOutcome"]),
        "Коментарий:": params["comment"],
        "Форма оплаты:": payment,
        "Тип:": "Выплата",
        "Дата:": close_date[0:16],
        "№:": number["number"] + 1,
    }
    return [result]
