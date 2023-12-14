from bd.model import (
    Session,
    Shop,
    Products,
    Documents,
    Employees,
    Message,
    Shift_Opening_Report,
)
from arrow import utcnow, get
from pprint import pprint
from .util import get_products, period_to_date, get_intervals


name = "Отчет 3".upper()
desc = ""
mime = "text"


class PeriodOpenDateInput:
    name = "Магазин"
    desc = "Выберите период"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "day", "name": "День"},
            {"id": "week", "name": "Неделя"},
            {"id": "fortnight", "name": "Две недели"},
            {"id": "month", "name": "Месяц"},
        ]

        return output


class OpenDateInput:
    desc = "Выберите дату начало пириода "
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
            output.append({"id": left, "name": left[0:10]})

        return output


class PeriodOpenDateInput:
    name = "Магазин"
    desc = "Выберите период"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "day", "name": "День"},
            {"id": "week", "name": "Неделя"},
            {"id": "fortnight", "name": "Две недели"},
            {"id": "month", "name": "Месяц"},
            {"id": "two months", "name": "Два месяца"},
        ]

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


def get_inputs(session: Session):
    return {
        # 'cash_income1': CachIncome1Input,
        # 'cash_income2': CachIncome2Input,
        "periodOpenDate": PeriodOpenDateInput,
        "openDate": OpenDateInput,
        "closeDate": CloseDateInput,
    }


def generate(session: Session):
    params = session.params["inputs"]["0"]

    since = get(params["openDate"]).replace(hour=3, minute=00).isoformat()

    until = get(params["closeDate"]).replace(hour=23, minute=00).isoformat()

    shops = [
        "20220501-DDCF-409A-8022-486441F27458",
        # '20200630-3E0D-4061-80C1-F7897E112F00',
        "20220501-9ADF-402C-8012-FB88547F6222",
        "20220501-3254-40E5-809E-AC6BB204D373",
        "20230214-33E5-4085-80A3-28C177E34112",
        "20220501-4D25-40AD-80DA-77FAE02A007E",
        "20220601-4E97-40A5-801B-1A29127AFA8B",
        "20220430-A472-40B8-8077-2EE96318B7E7",
        "20220201-19C9-40B0-8082-DF8A9067705D",
        "20220202-B042-4021-803D-09E15DADE8A4",
    ]
    x_type = ["SELL", "PAYBACK"]
    documents = Documents.objects(
        __raw__={
            "closeDate": {"$gte": since, "$lt": until},
            "shop_id": {"$in": shops},
            "x_type": {"$in": x_type},
            # 'transactions.commodityUuid': {'$in': products_uuid}
        }
    )
    # pprint(documents)
    _dict = {}
    sum_sell = 0
    sum_sell_1 = 0
    sum_sell_2 = 0
    sum_sell_3 = 0
    tester = []
    for doc in documents:
        for trans in doc["transactions"]:
            if trans["x_type"] == "REGISTER_POSITION":
                if doc["shop_id"] not in tester:
                    tester.append(doc["shop_id"])
                products = Products.objects(
                    __raw__={"shop_id": doc["shop_id"], "uuid": trans["commodityUuid"]}
                )
                for item in products:
                    sum_sell += int(trans["quantity"]) * int(trans["price"]) - int(
                        item["costPrice"] * int(trans["quantity"])
                    )
                    sum_sell_1 += int(item["costPrice"] * int(trans["quantity"]))
                    sum_sell_2 += trans["sum"]
                    sum_sell_3 += trans["quantity"]
    _dict["Начало пириода"] = session["params"]["inputs"]["0"]["openDate"][0:10]
    _dict["Окончание пириода"] = session["params"]["inputs"]["0"]["closeDate"][0:10]

    _dict["Вал:".upper()] = "{}".format(sum_sell)
    _dict["Оборот:".upper()] = "{}".format(sum_sell_1)
    _dict["Продано:".upper()] = "{}".format(sum_sell_2)
    _dict["ШТ:".upper()] = "{}".format(sum_sell_3)
    _dict["Доход:".upper()] = "{}".format(sum_sell_3 * 2)
    _dict["M"] = "{}".format(len(tester))

    for i in tester:
        shop_name = [i.name for i in Shop.objects(uuid=i)][0]
        pprint(shop_name)
    return [_dict]
