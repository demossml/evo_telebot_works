from bd.model import Shop, Products, Documents, Session, Employees
from .util import get_intervals, get_period, get_shops_user_id, get_shops
from pprint import pprint
from collections import OrderedDict

# from profilehooks import profile
from .inputs import (
    ReportSalesInput,
    ShopAllInput,
    GroupInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
)


name = "🛒 ОТЧЕТЫ ПО ПРОДАЖАМ ➡️"
desc = "ОТЧЕТЫ по ПРОДАЖАМ"
mime = "text"


# @Profile(stdout=False, filename="baseline.prof")
def get_inputs(session: Session):
    period = ["day", "week", "fortnight", "month"]
    if session.params["inputs"]["0"]:
        if "period" in session.params["inputs"]["0"]:
            if session.params["inputs"]["0"]["period"] == "day":
                return {}
            if session.params["inputs"]["0"]["period"] not in period:
                return {"openDate": OpenDatePastInput}
            else:
                return {"openDate": OpenDatePastInput, "closeDate": CloseDatePastInput}
        if session.params["inputs"]["0"]["report"] == "get_sales_by_day_of_the_week":
            shop_uuid = get_shops_user_id(session)
            if len(shop_uuid) > 0:
                return {"shop": ShopAllInput, "period": PeriodDateInput}
            else:
                return {
                    "period": PeriodDateInput,
                }
        if (
            session.params["inputs"]["0"]["report"]
            == "get_sales_by_shop_product_group_rub"
        ):
            shop_uuid = get_shops_user_id(session)
            if len(shop_uuid) > 0:
                return {
                    "shop": ShopAllInput,
                    "group": GroupInput,
                    "period": PeriodDateInput,
                }
            else:
                return {
                    "group": GroupInput,
                    "period": PeriodDateInput,
                }
        if (
            session.params["inputs"]["0"]["report"]
            == "get_sales_by_shop_product_group_unit"
        ):
            shop_uuid = get_shops_user_id(session)
            if len(shop_uuid) > 0:
                return {
                    "shop": ShopAllInput,
                    "group": GroupInput,
                    "period": PeriodDateInput,
                }
            else:
                return {
                    "group": GroupInput,
                    "period": PeriodDateInput,
                }

    else:
        return {"report": ReportSalesInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]
    period = get_period(session)

    since = period["since"]
    until = period["until"]

    shops = get_shops(session)
    shop_id = shops["shop_id"]
    shop_name = shops["shop_name"]

    x_type = ["SELL", "PAYBACK"]

    if "group" in params:
        if params["group"] == "all":
            products = Products.objects(
                __raw__={
                    "shop_id": {"$in": shop_id},
                }
            )
        else:
            products = Products.objects(
                __raw__={"shop_id": {"$in": shop_id}, "parentUuid": params["group"]}
            )
        products_uuid = [element.uuid for element in products]

    if params["report"] == "get_sales_by_day_of_the_week":
        payment_type = {
            "CARD": "Банковской картой",
            "ADVANCE": "Предоплатой (зачетом аванса)",
            "CASH": "Наличными средствами",
            "COUNTEROFFER": "Встречным предоставлением",
            "CREDIT": "Постоплатой (в кредит)",
            "ELECTRON": "Безналичными средствами",
            "UNKNOWN": "Неизвестно. По-умолчанию",
        }
        payment_type_sum_sell_total = {
            "CARD": 0,
            "ADVANCE": 0,
            "CASH": 0,
            "COUNTEROFFER": 0,
            "CREDIT": 0,
            "ELECTRON": 0,
            "UNKNOWN": 0,
        }
        sum_sell_total = 0
        result = []
        intervals = get_intervals(since, until, "days", 1)
        for since_, until_ in intervals:
            for shop in shop_id:
                _dict = {}

                documents_open_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": shop,
                    }
                ).first()
                if documents_open_session:
                    employees = Employees.objects(
                        uuid=documents_open_session.closeUserUuid
                    ).first()
                    last_name = employees.lastName
                    name_ = employees.name
                else:
                    last_name = ""
                    name_ = ""

                shop_ = Shop.objects(uuid__exact=shop).only("name").first()
                documents = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since_, "$lt": until_},
                        "shop_id": shop,
                        "x_type": "SELL",
                    }
                )
                if len(documents) > 0:
                    sum_sell = 0
                    payment_type_sum_sell = {
                        "CARD": 0,
                        "ADVANCE": 0,
                        "CASH": 0,
                        "COUNTEROFFER": 0,
                        "CREDIT": 0,
                        "ELECTRON": 0,
                        "UNKNOWN": 0,
                    }

                    for doc in documents:
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "DOCUMENT_CLOSE":
                                sum_sell += trans["sum"]
                                sum_sell_total += trans["sum"]
                            if trans["x_type"] == "PAYMENT":
                                payment_type_sum_sell[trans["paymentType"]] += trans[
                                    "sum"
                                ]
                                payment_type_sum_sell_total[
                                    trans["paymentType"]
                                ] += trans["sum"]

                    _dict["Магазин:"] = "{}:".format(shop_.name).upper()
                    _dict["Пордавец:"] = "{} {}:".format(last_name, name_).upper()
                    _dict["Дата:"] = since_[0:10]
                    _dict["Сумма:"] = "{} {}".format(sum_sell, "₽")

                    for k, v in payment_type_sum_sell.items():
                        if v > 0:
                            _dict[payment_type[k]] = "{} {}".format(v, "₽")

                else:
                    _dict["Магазин:"] = "{}:".format(shop_.name).upper()
                    _dict["Дата:"] = since_[0:10]
                    _dict["Сумма:"] = "{} {}".format(0, "₽")

                result.append(_dict)
        dict_total = {
            "Итого:".upper(): "",
            "Начало пириода:": since[0:10],
            "Окончание пириода:": until[0:10],
        }

        for k, v in payment_type_sum_sell_total.items():
            if v > 0:
                dict_total[payment_type[k]] = "{} {}".format(v, "₽")
        dict_total["Сумма:"] = "{} {}".format(sum_sell_total, "₽")
        result.append(dict_total)
        return result

    if params["report"] == "get_sales_by_shop_product_group_rub":
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": {"$in": shop_id},
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )
        _dict = {}

        for doc in documents:
            for trans in doc["transactions"]:
                if trans["x_type"] == "REGISTER_POSITION":
                    if trans["commodityUuid"] in products_uuid:
                        if trans["commodityName"] in _dict:
                            _dict[trans["commodityName"]] += trans["sum"]
                        else:
                            _dict[trans["commodityName"]] = trans["sum"]

        shop = Shop.objects(uuid__exact=shop_id[0]).only("name").first()
        _dict = dict(OrderedDict(sorted(_dict.items(), key=lambda t: -t[1])))
        total = 0
        _dict_total = {}
        for k, v in _dict.items():
            _dict_total[k] = "{} {}".format(v, "₽")
            total += int(v)
        _dict_total["Итого:"] = "{} {}".format(total, "₽")
        _dict_total["Магазин:"] = shop_name
        _dict_total["Начало пириода:"] = since[0:10]
        _dict_total["Окончание пириода:"] = until[0:10]
        return [_dict_total]

    if params["report"] == "get_sales_by_shop_product_group_unit":
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": {"$in": shop_id},
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )
        # pprint(documents)
        _dict = {}

        for doc in documents:
            for trans in doc["transactions"]:
                # pprint(trans)
                if trans["x_type"] == "REGISTER_POSITION":
                    if trans["commodityUuid"] in products_uuid:
                        if trans["commodityName"] in _dict:
                            _dict[trans["commodityName"]] += trans["quantity"]
                        else:
                            _dict[trans["commodityName"]] = trans["quantity"]

        _dict = dict(OrderedDict(sorted(_dict.items(), key=lambda t: -t[1])))

        total = 0
        _dict_total = {}
        for k, v in _dict.items():
            _dict_total[k] = "{} {}".format(v, "шт.")
            total += int(v)
        _dict_total["Итого:"] = "{} {}".format(total, "шт.")
        _dict_total["Магазин:"] = shop_name
        _dict_total["Начало пириода:"] = since[0:10]
        _dict_total["Окончание пириода:"] = until[0:10]

        return [_dict_total]
