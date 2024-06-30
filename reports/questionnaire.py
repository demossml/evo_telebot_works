from bd.model import Shop, Products, Documents, Session, Employees
from .util import (
    get_intervals,
    get_period,
    get_shops_user_id,
    get_shops,
    get_top_n_sales,
)
from pprint import pprint
from collections import OrderedDict


from .inputs import (
    ReportSalesInput,
    ShopAllInput,
    GroupInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
)

from io import BytesIO
import plotly.express as px
import io
import plotly.subplots as sp
import plotly.graph_objects as go
import math

name = "🛒 ОТЧЕТЫ ПО ПРОДАЖАМ ➡️"
desc = "ОТЧЕТЫ по ПРОДАЖАМ"
mime = "image_bytes"


def get_inputs(session: Session):
    # Получаем входные данные из сессии
    inputs = session.params.get("inputs", {}).get("0", {})

    # Если входных данных нет, возвращаем ввод для отчета по продажам
    if not inputs:
        return {"report": ReportSalesInput}

    # Извлекаем период и тип отчета из входных данных
    period = inputs.get("period", None)
    report_type = inputs.get("report", None)

    # Получаем идентификаторы магазинов пользователя
    shop_uuid = get_shops_user_id(session)
    # Создаем ввод для магазина, если у пользователя есть магазины
    shop_input = {"shop": ShopAllInput} if len(shop_uuid) > 0 else {}

    # Обработка вводных данных в зависимости от периода
    if period in ("day", "week", "fortnight", "month"):
        # Если период - день, возвращаем пустой ввод, в противном случае возвращаем ввод с датами
        return (
            {"openDate": OpenDatePastInput, "closeDate": CloseDatePastInput}
            if period != "day"
            else {}
        )
    # Если период не является одним из допустимых, возвращаем ввод с прошедшей датой
    elif period is not None:
        return {"openDate": OpenDatePastInput}

    # Обработка вводных данных в зависимости от типа отчета
    if report_type == "get_sales_by_day_of_the_week":
        # Возвращаем ввод для отчета по дням недели с учетом наличия магазинов
        return {"shop": ShopAllInput, "period": PeriodDateInput, **shop_input}
    elif report_type in (
        "get_sales_by_shop_product_group_rub",
        "get_sales_by_shop_product_group_unit",
    ):
        # Возвращаем ввод для отчета по продажам по магазинам, группам продуктов и периоду с учетом наличия магазинов
        return {
            "shop": ShopAllInput,
            "group": GroupInput,
            "period": PeriodDateInput,
            **shop_input,
        }
    # Возвращаем ввод для отчета по продажам по группам продуктов и периоду с учетом наличия магазинов
    else:
        return {"group": GroupInput, "period": PeriodDateInput, **shop_input}


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
        # Создаем базовый запрос с условием, что 'shop_id' находится в списке магазинов
        query = {"shop_id": {"$in": shop_id}}

        products_name = "все группы"
        # Если параметр 'group' не равен "all", добавляем условие для 'parentUuid' в запрос
        if params["group"] != "all":
            query["parentUuid"] = params["group"]
            products_name = (
                Products.objects(uuid=params["group"]).only("name").first().name
            )

        # Выполняем запрос к базе данных с использованием сформированного запроса
        products = Products.objects(__raw__=query)
        # Получаем список UUID продуктов из результата запроса
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
                _dict = {
                    "Магазин:": "{}:".format(
                        Shop.objects(uuid__exact=shop).only("name").first().name
                    ).upper()
                }
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

                    # _dict["Магазин:"] = "{}:".format(shop_.name).upper()
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

        return result, None

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
        # Сортируем словарь по убыванию количества продаж
        sorted_sales = get_top_n_sales(sales_data)

        if len(sorted_sales[0]) > 0:

            # Извлекаем названия магазина и суммы продаж
            shop_names = list(sorted_sales[0].keys())
            sum_sales_quantity = list(sorted_sales[0].values())
            sum_sales_quantity_total = sum(sorted_sales[0].values())

            # Создаем фигуру для гистограммы
            fig = px.bar(
                y=shop_names,
                x=sum_sales_quantity,
                title=f"Продажи в ₽. по {products_name}. Топ {sorted_sales[1]}.Начало/Окончание периода - {since[0:10]}/{until[0:10]}",
                labels={"y": "Магазин", "x": "Сумма продаж"},
                # Цвет фона графика
                # Дополнительные настройки могут быть добавлены по вашему усмотрению
            )
            # Настройки внешнего вида графика
            font_size = 24  # Задаем начальный размер шрифта

            pprint(font_size)
            # Настройки внешнего вида графика
            fig.update_layout(
                font=dict(size=font_size, family="Arial, sans-serif", color="black"),
                # plot_bgcolor="black",  # Цвет фона графика
            )

            # Добавляем аннотации с суммами продаж
            for i, value in enumerate(sum_sales_quantity):
                fig.add_annotation(
                    x=value,
                    y=shop_names[i],
                    text=f"{value:,}",  # Форматируем число с разделителями тысяч
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="black",
                    ax=40,
                    ay=0,
                )

            # Устанавливаем ориентацию осей
            fig.update_xaxes(title=f"Сумма продаж {sum_sales_quantity_total} ₽.")

            fig.update_yaxes(
                title=f"Магазин {shop_name}", autorange="reversed"
            )  # Разворачиваем ось Y

            # Сохраняем гистограмму в формате PNG в объект BytesIO
            image_buffer = io.BytesIO()

            target_width = 1700
            # target_height = 2000
            target_height = len(shop_names) * 54

            # Динамический расчет оптимальной ширины и высоты на основе количества магазинов
            dynamic_aspect_ratio = (
                len(shop_names) / 70
            )  # Пример: корректируйте это значение по своему усмотрению
            optimal_width = min(target_width, target_height / dynamic_aspect_ratio)
            optimal_height = min(target_height, target_width * target_height)

            # Сохраняем гистограмму в формате PNG с оптимальным разрешением
            fig.write_image(
                image_buffer, format="png", width=optimal_width, height=optimal_height
            )

            # Очищаем буфер изображения и перемещаем указатель в начало
            image_buffer.seek(0)
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

        return [total_info], image_buffer

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

        # Сортируем словарь с данными о продажах
        sorted_sales_data = dict(
            OrderedDict(sorted(sales_by_product.items(), key=lambda t: -t[1]))
        )

        # Сортируем словарь по убыванию количества продаж
        sorted_sales = get_top_n_sales(sales_by_product)

        if len(sorted_sales[0]) > 0:

            # Извлекаем названия магазина и суммы продаж
            shop_names = list(sorted_sales[0].keys())
            sum_sales_quantity = list(sorted_sales[0].values())
            sum_sales_quantity_total = sum(sorted_sales[0].values())

            # Создаем фигуру для гистограммы
            fig = px.bar(
                y=shop_names,
                x=sum_sales_quantity,
                title=f"Продажи в шт. по {products_name}. Топ {sorted_sales[1]}.Начало/Окончание периода - {since[0:10]}/{until[0:10]}",
                labels={"y": "Магазин", "x": "Сумма продаж"},
                # Цвет фона графика
                # Дополнительные настройки могут быть добавлены по вашему усмотрению
            )
            # Настройки внешнего вида графика
            font_size = 24  # Задаем начальный размер шрифта

            pprint(font_size)
            # Настройки внешнего вида графика
            fig.update_layout(
                font=dict(size=font_size, family="Arial, sans-serif", color="black"),
                # plot_bgcolor="black",  # Цвет фона графика
            )

            # Добавляем аннотации с суммами продаж
            for i, value in enumerate(sum_sales_quantity):
                fig.add_annotation(
                    x=value,
                    y=shop_names[i],
                    text=f"{value:,}",  # Форматируем число с разделителями тысяч
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="black",
                    ax=40,
                    ay=0,
                )

            # Устанавливаем ориентацию осей
            fig.update_xaxes(title=f"Сумма продаж {sum_sales_quantity_total}шт.")

            fig.update_yaxes(
                title=f"Магазин {shop_name}", autorange="reversed"
            )  # Разворачиваем ось Y

            # Сохраняем гистограмму в формате PNG в объект BytesIO
            image_buffer = io.BytesIO()

            target_width = 1700
            # target_height = 2000
            target_height = len(shop_names) * 54
            # pprint(len(shop_names))

            # Динамический расчет оптимальной ширины и высоты на основе количества магазинов
            dynamic_aspect_ratio = (
                len(shop_names) / 70
            )  # Пример: корректируйте это значение по своему усмотрению
            optimal_width = min(target_width, target_height / dynamic_aspect_ratio)
            optimal_height = min(target_height, target_width * target_height)

            # Сохраняем гистограмму в формате PNG с оптимальным разрешением
            fig.write_image(
                image_buffer, format="png", width=optimal_width, height=optimal_height
            )

            # Очищаем буфер изображения и перемещаем указатель в начало
            image_buffer.seek(0)

            # Вычисляем общее количество продаж
            total_quantity = sum(sorted_sales[0].values())

            # Создаем словарь для вывода результатов отчета
            report_data = {}

            # Добавляем данные о продажах в словарь результатов
            for product_name, quantity in sorted_sales_data.items():
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

            return [report_data], image_buffer
        else:
            return [
                {
                    "Магазин:": shop_name,
                    "Начало периода:": since[0:10],
                    "Окончание периода:": until[0:10],
                    "Итого:": " 0 шт.",
                }
            ]
