from bd.model import Session, Shop, Products, Documents, Employees, Message
from arrow import utcnow, get
from pprint import pprint
from .util import period_to_date, get_intervals

import telebot
from typing import List, Tuple

name = "Приемка/Списание"
desc = "Собирает данные о приемке товара"
mime = "text"


class ReportsInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "get_accept", "name": "Приемка"},
            {"id": "get_write_off", "name": "Списание"},
        )

        return output


class ShopInput:
    desc = "Выберите магазин из списка"
    type = "SELECT"

    def get_options(self, session: Session):
        _in = (
            "20220501-DDCF-409A-8022-486441F27458",
            # '20200630-3E0D-4061-80C1-F7897E112F00',
            "20220501-9ADF-402C-8012-FB88547F6222",
            "20220501-3254-40E5-809E-AC6BB204D373",
            "20230214-33E5-4085-80A3-28C177E34112",
            "20220501-4D25-40AD-80DA-77FAE02A007E",
            "20220601-4E97-40A5-801B-1A29127AFA8B",
            "20220430-A472-40B8-8077-2EE96318B7E7",
        )
        output = []
        for item in Shop.objects(uuid__in=_in):
            # pprint(item["name"])
            output.append({"id": item["uuid"], "name": item["name"]})

        return output


class PeriodInput:
    name = "Магазин"
    desc = "Выберите период"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "day", "name": "День"},
            {"id": "week", "name": "Неделя"},
            {"id": "fortnight", "name": "Две недели"},
            {"id": "month", "name": "Месяц"},
        )

        return output


class DayInput:
    desc = "Выберите дату"
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['0']['period'])
        since = period_to_date(session["params"]["inputs"]["0"]["period"])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        shop_id = session.params["inputs"]["0"]["shop"]
        # pprint(intervals)

        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": shop_id,
                "x_type": "ACCEPT",
            }
        )
        _in = [doc["openDate"] for doc in documents]
        for left, right in intervals:
            pprint(left)
            if left[0:10] in _in:
                output.append({"id": left, "name": left[0:10]})

        return output


class OpenDateInput:
    desc = "Выберите дату начало пириода "
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session["params"]["inputs"]["0"]["period"])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({"id": left, "name": left[0:10]})

        return output


class CloseDateInput:
    desc = "Выберите дату окончание пириода "
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = session["params"]["inputs"]["0"]["openDate"]
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)

        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({"id": left, "name": left[0:10]})

        return output


class DocumentsInput:
    desc = "Выберите дату"
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        params = session.params["inputs"]["0"]

        since = get(params["openDate"]).replace(hour=3, minute=00).isoformat()
        until = get(params["closeDate"]).replace(hour=23, minute=00).isoformat()
        shop_id = params["shop"]
        if params["report"] == "get_accept":
            pprint([i.name for i in Shop.objects(uuid=shop_id)][0])

            documents = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop_id,
                    "x_type": "ACCEPT",
                }
            )
        if params["report"] == "get_write_off":
            pprint([i.name for i in Shop.objects(uuid=shop_id)][0])

            documents = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop_id,
                    "x_type": "WRITE_OFF",
                }
            )
            # pprint(documents)
        for item in documents:
            output.append(
                {
                    "id": item["number"],
                    "name": get(item["closeDate"]).shift(hours=3).isoformat()[0:10],
                }
            )
        return output


def get_inputs(session: Session):
    return {
        "report": ReportsInput,
        "shop": ShopInput,
        "period": PeriodInput,
        "openDate": OpenDateInput,
        "closeDate": CloseDateInput,
        "number": DocumentsInput,
    }


def generate(session: Session):
    params = session.params["inputs"]["0"]

    shop_id = params["shop"]
    number = params["number"]
    documents = Documents.objects(
        __raw__={
            "number": int(number),
            "shop_id": shop_id,
        }
    )
    pprint(documents)
    _dict = {}
    _sum = 0
    for element in documents:
        for trans in element["transactions"]:
            if trans["x_type"] == "REGISTER_POSITION":
                _sum += int(trans["sum"])
                _dict.update(
                    {
                        trans["commodityName"]: "{}п./{}/{}".format(
                            trans["quantity"], trans["resultPrice"], trans["sum"]
                        )
                    }
                )
    _dict.update({"sum": _sum})

    return [_dict]
