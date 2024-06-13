from arrow import utcnow, get
from bd.model import Session, CashRegister, Documents, Shop
from pprint import pprint
from .inputs import (
    ShopAllInInput,
)
from .util import get_intervals, get_period, get_shops_user_id, get_shops


name = "💰🚬 Остаток в кассах ТТ ➡️".upper()
desc = "Остаток в кассе"
mime = "text"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    params = session.params["inputs"]["0"]

    # Получение информации о магазинах
    if params["shop"] == "all":
        shops_id = (
            "20220202-B042-4021-803D-09E15DADE8A4",
            "20220201-19C9-40B0-8082-DF8A9067705D",
        )
    else:
        shops_id = [params["shop"]]

    report_data = {}
    sum_ = 0
    cash = CashRegister.objects()
    if cash:
        for doc in cash:
            pprint(doc["cash"])
            if doc["x_type"] == "CASH_INCOME":
                sum_ += doc["cash"]

            if doc["x_type"] == "CASH_OUTCOME":
                sum_ -= doc["cash"]
    else:
        sum_ = 0

    report_data.update({"I have": sum_})
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
                report_data.update({shop.name: int(trans["cash"])})
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
                        report_data[shop.name] -= trans["sum"]

            if doc["x_type"] == "CASH_INCOME":
                for trans in doc["transactions"]:
                    if trans["x_type"] == "CASH_INCOME":
                        report_data[shop.name] += trans["sum"]
            if doc["x_type"] == "SELL":
                for trans in doc["transactions"]:
                    if trans["x_type"] == "PAYMENT":
                        if trans["paymentType"] == "CASH":
                            report_data[shop.name] += trans["sum"]
            if doc["x_type"] == "PAYBACK":
                for trans in doc["transactions"]:
                    if trans["x_type"] == "PAYMENT":
                        if trans["paymentType"] == "CASH":
                            report_data[shop.name] -= trans["sum"]

    return [report_data]
