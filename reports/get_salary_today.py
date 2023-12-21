from bd.model import Shop, Products, Documents, Session, Employees, GroupUuidAks
from .util import (
    get_shops_uuid_user_id,
    get_period,
    get_aks_salary,
    get_shops,
    get_intervals,
    get_mot_salary,
    get_plan_bonus,
    get_salary,
    get_surcharge,
    get_total_salary,
    get_period_day,
)
from pprint import pprint
from collections import OrderedDict
import matplotlib.pyplot as plt


from arrow import utcnow, get


name = "🤑🤑🤑 Зарплата ➡️".upper()
desc = ""
mime = "text"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().replace(hour=20, minute=59).isoformat()

    result = []
    name = Employees.objects(lastName=str(session.user_id)).only("name").first()
    user = Employees.objects(lastName=str(session.user_id)).only("uuid").first()
    # pprint(name.name)
    # pprint(user.uuid)

    documents_open_session = Documents.objects(
        __raw__={
            "closeDate": {"$gte": since, "$lt": until},
            "openUserUuid": user.uuid,
            "x_type": "OPEN_SESSION",
        }
    ).first()
    pprint(documents_open_session)
    if documents_open_session:
        shop = Shop.objects(uuid=documents_open_session.shop_id).only("name").first()
        # pprint(shop.name)

        documents_aks = (
            GroupUuidAks.objects(
                __raw__={
                    "closeDate": {"$lte": until[:10]},
                    "shop_id": documents_open_session.shop_id,
                    "x_type": "MOTIVATION_PARENT_UUID",
                }
            )
            .order_by("-closeDate")
            .first()
        )
        pprint(documents_aks)
        pprint(documents_open_session.shop_id)
        pprint(documents_aks.parentUuids)
        group = Products.objects(
            __raw__={
                "shop_id": documents_open_session.shop_id,
                # 'group': True,
                "parentUuid": {"$in": documents_aks.parentUuids},
            }
        )

        products_uuid = [i.uuid for i in group]

        pprint(products_uuid)
        documents_sale = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": documents_open_session.shop_id,
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )
        _dict = {}
        sum_sales = 0
        # last_time = (
        #     Documents.objects(
        #         __raw__={
        #             "closeDate": {"$gte": since, "$lt": until},
        #             "shop_id": documents_open_session.shop_id,
        #             "x_type": "SELL",
        #             "transactions.commodityUuid": {"$in": products_uuid},
        #         }
        #     )
        #     .order_by("-closeDate")
        #     .only("closeDate")
        #     .first()
        # )
        for doc in documents_sale:
            for trans in doc["transactions"]:
                if trans["x_type"] == "REGISTER_POSITION":
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

        sho_id = doc["shop_id"]

        total_salary = get_total_salary(str(session.user_id), sho_id, since, until)
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
                "Магазин:".upper(): shop.name.upper(),
                "Дата:".upper(): until[:10],
                # "Время выгрузки": last_time.closeDate[12:19],
                "Итго зарплата".upper(): "{}₱".format(total_salary["total_salary"]),
            }
        )
    result.append(
        {"Дата:".upper(): until[:10], name.name.upper(): "Сегодня не работает".upper()}
    )

    return result
