# Получить продажи по группе товаров по одному магазину в штуках по наименованию
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id,  id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from bd.model import Session, Shop, Products, Documents
from arrow import utcnow
from pprint import pprint
from .util import get_shops_user_id
from collections import OrderedDict

name = " 💨💨💨 Fyzzi/Электро ➡️".upper()
desc = "Генерирует отчет по продажам в шт. по электронкам в шт"
mime = "text"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    shops = get_shops_user_id(session)
    shops_id = [v.uuid for v in shops]
    pprint(shops_id)
    group_id = [
        "78ddfd78-dc52-11e8-b970-ccb0da458b5a",
        "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
        "0627db0b-4e39-11ec-ab27-2cf05d04be1d",
        "2b8eb6b4-92ea-11ee-ab93-2cf05d04be1d",
        "8a8fcb5f-9582-11ee-ab93-2cf05d04be1d",
        "97d6fa81-84b1-11ea-b9bb-70c94e4ebe6a",
        "ad8afa41-737d-11ea-b9b9-70c94e4ebe6a",
        "568905bd-9460-11ee-9ef4-be8fe126e7b9",
        "568905be-9460-11ee-9ef4-be8fe126e7b9",
    ]

    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().isoformat()

    products = Products.objects(
        __raw__={"parentUuid": {"$in": group_id}, "shop_id": {"$in": shops_id}}
    ).only("uuid")

    products_uuid = [element.uuid for element in products]
    result = []
    _dict = {}
    for shop in shops:
        result_shop = {}
        shop_name = [i.name for i in Shop.objects(uuid=shop["uuid"])][0]
        result_shop.update({"ТТ": shop_name})
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": shop["uuid"],
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )

        for doc in documents:
            for trans in doc["transactions"]:
                # pprint(77)
                if trans["x_type"] == "REGISTER_POSITION":
                    # pprint(88)
                    if trans["commodityUuid"] in products_uuid:
                        # pprint({trans['commodityName']: trans['quantity']})
                        if trans["commodityName"] in _dict:
                            _dict[trans["commodityName"]] += trans["quantity"]
                            if trans["commodityName"] in result_shop:
                                result_shop[trans["commodityName"]] += trans["quantity"]
                            else:
                                result_shop[trans["commodityName"]] = trans["quantity"]
                        else:
                            # pprint({trans['commodityName']: trans['quantity']})
                            _dict[trans["commodityName"]] = trans["quantity"]
                            result_shop[trans["commodityName"]] = trans["quantity"]

        # pprint(result_shop)
        if len(result_shop) > 1:
            result.append(result_shop)
    # pprint(result)

    _dict = dict(OrderedDict(sorted(_dict.items(), key=lambda t: -t[1])))

    total = 0
    for k, v in _dict.items():
        total += int(v)
    _dict["Итого:"] = total
    result.append({"⬇️Итого по всем тт".upper(): "⬇️".upper()})
    result.append(_dict)
    return result
