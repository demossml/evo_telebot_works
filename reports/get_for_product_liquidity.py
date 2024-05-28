import json
from pprint import pprint
from bd.model import Session, Documents, Products
from arrow import utcnow, get
from .inputs import ShopAllInput
from .util import json_to_xls_format_change

import logging

logger = logging.getLogger(__name__)


name = "Запрос ликвидности прод."
desc = "Запрос ликвидности прод."
mime = "file"


class FileInput:
    name = "Файл"
    desc = "Отправте файл в формате xls"
    type = "FILE"


def get_inputs(session: Session):
    return {"shop_id": ShopAllInput, "file": FileInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]

    shop_id = params["shop_id"]
    logger.info(shop_id)

    x_type = ("SELL", "PAYBACK")

    date_file_ = params["file"]

    # logger.info(date_file_)

    def get_sales(date_file: list) -> dict:

        # Создаем пустой словарь для хранения результатов
        sales_by_product_7 = []

        sales_by_product_14 = []

        sales_by_product_21 = []

        sales_by_product_31 = []

        sales_by_product_all = []

        sales_by_product_none = []

        for item in date_file:
            sum_sale_ = 0
            # Получаем продукты для магазина и группы товаров
            products = Products.objects(
                __raw__={"shop_id": shop_id, "name": item["name"]}
            ).first()
            product = products.uuid
            product_quantity = products.quantity

            # Рассчитываем временные интервалы с использованием UTC времени
            since = utcnow().to("local").shift(months=-1).isoformat()
            # pprint(since)
            until = utcnow().to("local").isoformat()

            documents = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop_id,
                    "x_type": {"$in": x_type},
                    "transactions.commodityUuid": product,
                }
            )

            if len(documents) > 0:
                # Обходим документы
                for doc in documents:
                    for trans in doc["transactions"]:
                        # Проверяем тип транзакции
                        if (
                            trans["x_type"] == "REGISTER_POSITION"
                            and trans["commodityUuid"] == product
                        ):

                            sum_sale_ += trans["quantity"]
            sum_q = item["sum"] * product_quantity
            cost_price_summ = sum_sale_ * item["sum"]
            # pprint(cost_price_summ)
            sales_days = (
                round(sum_q / (cost_price_summ / 30)) if sum_sale_ > 0 else None
            )
            # pprint(sales_days)

            average_sales = round(sum_sale_)

            if sales_days is not None:
                if sales_days <= 7:
                    sales_by_product_7.append(
                        {
                            "name": item["name"],
                            "sum": sum_q,
                            "average_sales": average_sales,
                            "sales_days": sales_days,
                        }
                    )
                if sales_days <= 14:
                    sales_by_product_14.append(
                        {
                            "name": item["name"],
                            "sum": sum_q,
                            "average_sales": average_sales,
                            "sales_days": sales_days,
                        }
                    )
                if sales_days <= 21:
                    sales_by_product_21.append(
                        {
                            "name": item["name"],
                            "sum": sum_q,
                            "average_sales": average_sales,
                            "sales_days": sales_days,
                        }
                    )
                if sales_days <= 31:
                    sales_by_product_31.append(
                        {
                            "name": item["name"],
                            "sum": sum_q,
                            "average_sales": average_sales,
                            "sales_days": sales_days,
                        }
                    )
                if sales_days > 31:
                    sales_by_product_all.append(
                        {
                            "name": item["name"],
                            "sum": sum_q,
                            "average_sales": average_sales,
                            "sales_days": sales_days,
                        }
                    )
            else:
                sales_by_product_none.append(
                    {
                        "name": item["name"],
                        "sum": sum_q,
                        "average_sales": average_sales,
                        "sales_days": sales_days,
                    }
                )

        # Логгирование результатов
        result = [
            sales_by_product_7,
            sales_by_product_14,
            sales_by_product_21,
            sales_by_product_31,
            sales_by_product_all,
            sales_by_product_none,
        ]

        return result

    data_result = get_sales(date_file_)
    list_book = []
    for i in data_result:
        list_book.append(json_to_xls_format_change(i))
    # pprint(list_book)
    return list_book
