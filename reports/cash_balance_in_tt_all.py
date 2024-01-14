from arrow import utcnow, get
from bd.model import Session, CashRegister, Documents, Shop
from pprint import pprint
from .inputs import (
    ShopAllInput,
)
from .util import get_shops


name = "💰🚬 ₱ в кассах ТТ ➡️".upper()
desc = "Остаток в кассе"
mime = "text"


def get_inputs(session: Session):
    return {"shop": ShopAllInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]

    # Получение информации о магазинах
    shops = get_shops(session)
    shops_id = shops["shop_id"]
    pprint(shops_id)

    report_data = {}
    sum_ = 0

    for shop_id in shops_id:
        shop = Shop.objects(uuid=shop_id).only("name").first()

        document_fprint = (
            Documents.objects(
                __raw__={
                    "shop_id": shop_id,
                    "x_type": "FPRINT",
                    "transactions.x_type": "FPRINT_Z_REPORT",
                },
            )
            .order_by("-closeDate")
            .first()
        )
        if document_fprint:
            for trans in document_fprint.transactions:
                pprint(trans["cash"])
                report_data.update({shop.name: round(float(trans["cash"]), 2)})
            since = document_fprint.closeDate
            until = utcnow().isoformat()
            pprint(report_data)
            documents = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop_id,
                },
            )
        else:
            documents = Documents.objects(
                __raw__={"shop_id": shop_id},
            )
        for doc in documents:
            if doc["x_type"] == "CASH_OUTCOME":
                for trans in doc["transactions"]:
                    if trans["x_type"] == "CASH_OUTCOME":
                        report_data[shop.name] -= round(float(trans["sum"]), 2)

            if doc["x_type"] == "CASH_INCOME":
                for trans in doc["transactions"]:
                    if trans["x_type"] == "CASH_INCOME":
                        report_data[shop.name] += round(float(trans["sum"]), 2)
            if doc["x_type"] == "SELL":
                for trans in doc["transactions"]:
                    if trans["x_type"] == "PAYMENT":
                        if trans["paymentType"] == "CASH":
                            pprint(trans["sum"])
                            report_data[shop.name] += round(float(trans["sum"]), 2)
            if doc["x_type"] == "PAYBACK":
                for trans in doc["transactions"]:
                    if trans["x_type"] == "PAYMENT":
                        if trans["paymentType"] == "CASH":
                            report_data[shop.name] -= round(float(trans["sum"]), 2)

    for k, v in report_data.items():
        report_data.update({k: f"{v}₱"})

    last_time = (
        Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
            }
        )
        .order_by("-closeDate")
        .only("closeDate")
        .first()
    )
    if last_time:
        time = get(last_time.closeDate).shift(hours=3).isoformat()[11:19]
        pprint(time)
    else:
        time = 0

    report_data.update(
        {
            "🕰️ Время выгрузки ->".upper(): time,
        }
    )

    return [report_data]
