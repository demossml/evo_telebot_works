from arrow import utcnow, get
from bd.model import Session, CashRegister
from pprint import pprint

name = "💰💰💰 Остаток в кассе ➡️".upper()
desc = "Остаток в кассе"
mime = "text"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    params = session.params["inputs"]["0"]

    sum_ = 0

    cash = CashRegister.objects()
    if cash:
        for doc in cash:
            pprint(doc["cash"])
            if doc["x_type"] == "CASH_INCOME":
                sum_ += doc["cash"]

            if doc["x_type"] == "CASH_OUTCOME":
                sum_ -= doc["cash"]

        return [
            {
                "Сумма": f"{sum_}₽",
            }
        ]
    else:
        return [
            {
                "Сумма": f"{0}₽",
            }
        ]
