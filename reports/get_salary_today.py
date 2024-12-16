from bd.model import Shop, Products, Documents, Session, Employees, GroupUuidAks
from .util import (
    get_total_salary,
)
from pprint import pprint
from collections import OrderedDict
from evotor.evotor import evo


from arrow import utcnow, get


name = "🤑🤑🤑 Зарплата ➡️".upper()
desc = ""
mime = "text"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    # Получаем текущее локальное время один раз
    now = utcnow().to("local")

    # Формируем начало и конец дня
    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().replace(hour=23, minute=59).isoformat()
    pprint(since)

    result = []
    name = Employees.objects(lastName=str(session.user_id)).only("name").first()
    user = Employees.objects(lastName=str(session.user_id)).only("uuid").first()

    shops_id = evo.get_shops_uuid()
    # pprint(shops_id)

    documents_open_session = evo.get_first_open_session(
        shops_id, since, until, user.uuid
    )
    # pprint(documents_open_session)

    # documents_open_session = Documents.objects(
    #     __raw__={
    #         "closeDate": {"$gte": since, "$lt": until},
    #         "openUserUuid": "20240924-4BDE-4056-8087-968282CB45C9",
    #         "x_type": "OPEN_SESSION",
    #     }
    # ).first()

    # pprint(documents)

    if documents_open_session is not None:
        shop_name = evo.get_shop_name(documents_open_session["storeUuid"])

        documents_aks = (
            GroupUuidAks.objects(
                __raw__={
                    "closeDate": {"$lte": until[:10]},
                    "shop_id": documents_open_session["storeUuid"],
                    "x_type": "MOTIVATION_PARENT_UUID",
                }
            )
            .order_by("-closeDate")
            .first()
        )
        # pprint(documents_aks["parentUuids"])

        # group = Products.objects(
        #     __raw__={
        #         "shop_id": documents_open_session["storeUuid"],
        #         # 'group': True,
        #         "parentUuid": {"$in": documents_aks.parentUuids},
        #     }
        # )

        products_uuid = evo.get_products_by_group(
            documents_open_session["storeUuid"], documents_aks["parentUuids"]
        )

        documents_sale = evo.get_documents_by_products(
            documents_open_session["storeUuid"], since, until
        )
        # pprint(documents_sale)

        _dict = {}
        sum_sales = 0

        for doc in documents_sale:
            for trans in doc["transactions"]:
                if trans["type"] == "REGISTER_POSITION":
                    if trans["commodityUuid"] in products_uuid:
                        if trans["commodityName"] in _dict:
                            _dict[trans["commodityName"]] += trans["sum"]
                            sum_sales += trans["sum"]
                        else:
                            _dict[trans["commodityName"]] = trans["sum"]
                            sum_sales += trans["sum"]

        _dict = dict(OrderedDict(sorted(_dict.items(), key=lambda t: -t[1])))
        _dict_total = {}
        for k, v in _dict.items():
            _dict_total[k] = "{}₽".format(v)

        result.append(_dict_total)

        sho_id = doc["storeUuid"]

        total_salary = get_total_salary(str(session.user_id), sho_id, since, until, evo)
        result.append(
            {
                "Продажа аксс:".upper(): "{}₱".format(
                    total_salary["accessory_sum_sell"]
                ),
                "bonus за аксс:".upper(): "{}₱".format(total_salary["bonus_accessory"]),
                "bonus за мотиа. тов.:".upper(): "{}₱".format(
                    total_salary["bonus_motivation"]
                ),
                "План по Электронкам:".upper(): "{}₱".format(
                    total_salary["plan_motivation_prod"]
                ),
                "Продажи по Электронкам:".upper(): "{}₱".format(
                    total_salary["sales_motivation_prod"]
                ),
                "bonus за вып. плана:".upper(): "{}₱".format(
                    total_salary["bonus_motivation_prod"]
                ),
                "percent за аксс:".upper(): "{}%".format(5),
                "Оклад:".upper(): "{}₱".format(total_salary["salary"]),
                "Доплата:".upper(): "{}₱".format(total_salary["surcharge"]),
                "Продавец:".upper(): name.name.upper(),
                "Магазин:".upper(): shop_name.upper(),
                "Дата:".upper(): until[:10],
                "Итго зарплата".upper(): "{}₱".format(total_salary["total_salary"]),
            }
        )
        return result
    result.append(
        {"Дата:".upper(): until[:10], name.name.upper(): "Сегодня не работает".upper()}
    )

    return result


# {shop_id: "20190327-A48C-407F-801F-DA33CB4FBBE9", x_type: "OPEN_SESSION"}
# "20230929-E4B5-4056-800A-82A936C4D5F5"
