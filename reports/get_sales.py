from bd.model import Shop, Products, Documents, Session, Employees
from .util import get_intervals, get_period, get_shops_user_id, get_shops
from pprint import pprint
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


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


def get_inputs(session: Session):
    period = ("day", "week", "fortnight", "month")
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
    # Получение параметров из сессии
    params = session.params["inputs"]["0"]

    period = get_period(session)
    since = period["since"]
    until = period["until"]

    # Получение информации о магазинах
    shops = get_shops(session)
    shop_id = shops["shop_id"]
    shop_name = shops["shop_name"]

    # Типы транзакций
    x_type = ["SELL", "PAYBACK"]

    # Получение списка продуктов в зависимости от параметра 'group'
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
        # Инициализация словарей для сумм продаж и типов оплаты
        payment_type = {
            "CARD": "Банковской картой",
            "ADVANCE": "Предоплатой (зачетом аванса)",
            "CASH": "Наличными средствами",
            "COUNTEROFFER": "Встречным предоставлением",
            "CREDIT": "Постоплатой (в кредит)",
            "ELECTRON": "Безналичными средствами",
            "UNKNOWN": "Неизвестно. По-умолчанию",
        }
        payment_type_sum_sell_total = {ptype: 0 for ptype in payment_type}
        sum_sell_total = 0
        result = []
        intervals = get_intervals(since, until, "days", 1)
        for since_, until_ in intervals:
            for shop in shop_id:
                _dict = {}
                # Получаем документы с открытой сессией
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
                # Получаем документы по продажам
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

        # Добавляем итоговую информацию в результат
        dict_total = {
            "Итого:".upper(): "",
            "Начало пириода:": since[0:10],
            "Окончание пириода:": until[0:10],
        }
        # Добавляем информацию по типам оплаты в результат, если есть продажи
        for k, v in payment_type_sum_sell_total.items():
            if v > 0:
                dict_total[payment_type[k]] = "{} {}".format(v, "₽")
        dict_total["Сумма:"] = "{} {}".format(sum_sell_total, "₽")
        result.append(dict_total)
        return result

    # Проверяем условие "report" для определения выполняемой задачи
    if params["report"] == "get_sales_by_shop_product_group_rub":
        # Фильтруем документы в базе данных MongoDB
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": {"$in": shop_id},
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )

        # Создаем словарь для хранения данных о продажах
        sales_data = {}

        # Обработка документов
        for doc in documents:
            for trans in doc["transactions"]:
                if trans["x_type"] == "REGISTER_POSITION":
                    if trans["commodityUuid"] in products_uuid:
                        commodity_name = trans["commodityName"]
                        sale_sum = trans["sum"]

                        # Добавляем данные в словарь сумм продаж по товару
                        if commodity_name in sales_data:
                            sales_data[commodity_name] += sale_sum
                        else:
                            sales_data[commodity_name] = sale_sum

        # Получаем информацию о магазине
        shop = Shop.objects(uuid__exact=shop_id[0]).only("name").first()

        # Сортируем словарь с данными о продажах
        sorted_sales_data = dict(
            OrderedDict(sorted(sales_data.items(), key=lambda t: -t[1]))
        )

        # Вычисляем общую сумму продаж
        total_sales = sum(sorted_sales_data.values())

        # Создаем словарь с общей информацией
        total_info = {}
        for k, v in sorted_sales_data.items():
            total_info[k] = f"{v} ₽"
        total_info["Итого:"] = f"{total_sales} ₽"
        total_info["Магазин:"] = shop.name
        total_info["Начало периода:"] = since[0:10]
        total_info["Окончание периода:"] = until[0:10]

        return [total_info]
    if params["report"] == "get_sales_by_shop_product_group_unit":
        # Фильтруем документы из базы данных
        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": {"$in": shop_id},
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )

        # Создаем пустой словарь для хранения результатов
        sales_by_product = {}

        # Обходим документы
        for doc in documents:
            for trans in doc["transactions"]:
                # Проверяем тип транзакции
                if (
                    trans["x_type"] == "REGISTER_POSITION"
                    and trans["commodityUuid"] in products_uuid
                ):
                    commodity_name = trans["commodityName"]
                    quantity = trans["quantity"]
                    # Если товар уже есть в словаре, увеличиваем его количество, иначе добавляем
                    if commodity_name in sales_by_product:
                        sales_by_product[commodity_name] += quantity
                    else:
                        sales_by_product[commodity_name] = quantity

        # Сортируем словарь по убыванию количества продаж
        sorted_sales = dict(
            OrderedDict(sorted(sales_by_product.items(), key=lambda t: -t[1]))
        )
        pprint(sales_by_product)
        # Извлекаем названия продуктов и количество
        # product_names = list(sales_by_product.keys())
        # quantities = list(sales_by_product.values())

        # # Создаем круговую диаграмму
        # plt.figure(figsize=(10, 10))
        # plt.pie(quantities, labels=product_names, autopct="%1.1f%%", startangle=140)
        # plt.axis("equal")  # Задаем равное соотношение сторон для круга

        # # Сохраняем диаграмму в файл
        # plt.savefig("круговая_диаграмма.png")

        # # Показываем диаграмму
        # plt.show()

        # Вычисляем общее количество продаж
        total_quantity = sum(sorted_sales.values())

        # Создаем словарь для вывода результатов отчета
        report_data = {}

        # Добавляем данные о продажах в словарь результатов
        for product_name, quantity in sorted_sales.items():
            report_data.update({product_name: f"{quantity} шт."})

        # Добавляем общее количество продаж в результаты
        report_data.update({"Итого:": f"{total_quantity} шт."})

        report_data.update(
            {
                "Магазин:": shop_name,
                "Начало периода:": since[0:10],
                "Окончание периода:": until[0:10],
            }
        )

        return [report_data]
