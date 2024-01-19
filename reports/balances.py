from arrow import utcnow
from bd.model import Session, CashRegister
from pprint import pprint
from .util import cash

name = "Balance ➡️".upper()
desc = "Выплата"
mime = "text"


class CashRegistraterBagrationaInput:
    desc = "Напишите от ₱ касса Багратиона  ✍️".upper()
    type = "MESSAGE"


class RemainderBagrationaInput:
    desc = "Напишите от ₱ остаток Багратиона  ✍️".upper()
    type = "MESSAGE"


class CashRegistraterSkalaInput:
    desc = "Напишите от ₱ касса Скала  ✍️".upper()
    type = "MESSAGE"


class RemainderSkalaInput:
    desc = "Напишите от ₱ остаток Скала ✍️".upper()
    type = "MESSAGE"


class RSlaInput:
    desc = "Напишите от ₱ Р/С ✍️".upper()
    type = "MESSAGE"


class DutyeInput:
    desc = "Напишите ₱ долг ✍️".upper()
    type = "MESSAGE"


class ValInput:
    desc = "Напишите ₱ вал ✍️".upper()
    type = "MESSAGE"


def get_inputs(session: Session):
    return {
        "CashRegistraterBagrationa": CashRegistraterBagrationaInput,
        "RemainderBagrationa": RemainderBagrationaInput,
        "CashRegistraterSkala": CashRegistraterSkalaInput,
        "RemainderSkala": RemainderSkalaInput,
        "RS": RSlaInput,
        "duty": DutyeInput,
    }


def generate(session: Session):
    report_data = []
    params = session.params["inputs"]["0"]

    cash_ = cash()

    balance_data = {
        "касса Багратиона:".upper(): int(params["CashRegistraterBagrationa"]),
        "касса Скала:".upper(): int(params["CashRegistraterSkala"]),
        "остаток Багратиона:".upper(): int(params["RemainderBagrationa"]),
        "остаток Скала:".upper(): int(params["RemainderSkala"]),
        "Р/С:".upper(): int(params["RS"]),
        "У Меня": int(cash_),
    }

    # Summing the values
    total_sum = sum(balance_data.values())

    balance_data.update(
        {
            "долг:".upper(): params["duty"],
            "Итог:".upper(): int(total_sum) - int(params["duty"]),
        }
    )
    for k, v in balance_data.items():
        balance_data.update({k: f"{v}₱"})

    report_data.append(balance_data)
    return report_data
