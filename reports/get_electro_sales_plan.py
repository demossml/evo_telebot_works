# Получить план продажи по группе товаров по всем магазинам в руб.
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id, id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from bd.model import Session, Shop, Plan, Products, Documents, TimeSync
from arrow import utcnow, get
from pprint import pprint
from .util import (
    last_time,
    get_shops_in,
    generate_plan,
    generate_plan_,
    get_shops_user_id,
    get_shops_uuid_user_id,
    get_plan,
    analyze_sales_parallel,
)
import plotly.express as px
from io import BytesIO
import time
import concurrent.futures
from collections import defaultdict

name = "💹 План по Электронкам ➡️".upper()
desc = "Генерирует отчет по продажам в шт. по одной группе товаров в одном магазине за фиксированный период"
mime = "image_bytes"


def get_inputs(session: Session):
    return {}


def generate(session: Session) -> list[dict]:
    start_time = time.time()

    # # Группы товаров для анализа продаж
    # group_id = (
    #     "78ddfd78-dc52-11e8-b970-ccb0da458b5a",
    #     "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
    #     "0627db0b-4e39-11ec-ab27-2cf05d04be1d",
    #     "2b8eb6b4-92ea-11ee-ab93-2cf05d04be1d",
    #     "8a8fcb5f-9582-11ee-ab93-2cf05d04be1d",
    #     "97d6fa81-84b1-11ea-b9bb-70c94e4ebe6a",
    #     "ad8afa41-737d-11ea-b9b9-70c94e4ebe6a",
    #     "568905bd-9460-11ee-9ef4-be8fe126e7b9",
    #     "568905be-9460-11ee-9ef4-be8fe126e7b9",
    # )

    # # Определение временного периода для анализа
    # since_2 = utcnow().replace(hour=3, minute=00).isoformat()
    # until_2 = utcnow().isoformat()

    # _dict_2 = {}
    # # Словарь для хранения данных о продажах по магазинам
    # sales_data = {}
    # dict_last_time = {}
    # for shop in get_shops_user_id(session):
    #     dict_last_time.update(last_time(shop["uuid"]))
    #     since = utcnow().replace(hour=3, minute=00).isoformat()
    #     until = utcnow().replace(hour=20, minute=59).isoformat()

    #     # Получение данных о планах продаж для магазина
    #     plan_ = Plan.objects(
    #         __raw__={
    #             "closeDate": {"$gte": since, "$lt": until},
    #             "shop_id": shop["uuid"],
    #         }
    #     )
    #     # pprint(plan_)
    #     if len(plan_) > 0:
    #         # pprint(1)
    #         plan = Plan.objects(
    #             __raw__={
    #                 "closeDate": {"$gte": since, "$lt": until},
    #                 "shop_id": shop["uuid"],
    #             }
    #         ).first()
    #     else:
    #         generate_plan()

    #         plan = Plan.objects(
    #             __raw__={
    #                 "closeDate": {"$gte": since, "$lt": until},
    #                 "shop_id": shop["uuid"],
    #             }
    #         ).first()

    #     # Получение списка продуктов, относящихся к группам товаров
    #     products = Products.objects(
    #         __raw__={"shop_id": shop["uuid"], "parentUuid": {"$in": group_id}}
    #     )

    #     # Формирование списка идентификаторов продуктов
    #     products_uuid = [element.uuid for element in products]

    #     # Типы операций для анализа (продажи и возвраты)
    #     x_type = ("SELL", "PAYBACK")

    #     # Получение документов о продажах и возвратах для продуктов
    #     documents_2 = Documents.objects(
    #         __raw__={
    #             "closeDate": {"$gte": since_2, "$lt": until_2},
    #             "shop_id": shop["uuid"],
    #             "x_type": {"$in": x_type},
    #             "transactions.commodityUuid": {"$in": products_uuid},
    #         }
    #     )

    #     sum_sell_today = 0
    #     # Вычисление суммы продаж за текущий период
    #     for doc_2 in documents_2:
    #         for trans_2 in doc_2["transactions"]:
    #             if trans_2["x_type"] == "REGISTER_POSITION":
    #                 if trans_2["commodityUuid"] in products_uuid:
    #                     sum_sell_today += trans_2["sum"]

    #     if sum_sell_today > 0:
    #         sales_data.update({shop["name"]: sum_sell_today})

    #     # pprint(sales_data)

    #     # Добавление данных о продажах для текущего магазина
    #     if int(sum_sell_today) >= int(plan.sum):
    #         symbol = "✅"
    #     else:
    #         symbol = "🔴"

    #     # Формирование информации о планах и фактических продажах

    #     _dict_2[
    #         "{}{}".format(symbol, shop["name"][:9]).upper()
    #     ] = "пл.{}₽/пр.{}₽".format(int(plan.sum), int(sum_sell_today))
    # # end_time = time.time()
    # # execution_time = end_time - start_time
    # # print(f"Время выполнения функции sync_evo: {execution_time:.2f} секунд")

    # # Извлекаем названия магазина и суммы продаж
    # shop_names = list(sales_data.keys())
    # sum_sales_ = list(sales_data.values())
    # # Создаем фигуру для круговой диаграммы
    # fig = px.pie(
    #     names=shop_names,
    #     values=sum_sales_,
    #     title="Доля выручки по Электронкам  по магазинам",
    #     labels={"names": "Магазины", "values": "Выручка"},
    #     # Цвет фона графика
    # )

    # # Настройки внешнего вида графика
    # fig.update_layout(
    #     title="Продажи  по Электронкам по магазинам",
    #     font=dict(size=18, family="Arial, sans-serif", color="black"),
    #     # plot_bgcolor="black",  # Цвет фона графика
    # )

    # # Сохраняем диаграмму в формате PNG в объект BytesIO
    # image_buffer = BytesIO()

    # fig.write_image(image_buffer, format="png", width=700, height=700)

    # # Очищаем буфер изображения и перемещаем указатель в начало
    # image_buffer.seek(0)
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(f"Время выполнения функции sync_evo: {execution_time:.2f} секунд")
    # return [_dict_2, dict_last_time], image_buffer

    data_resul = {}
    data_sale = analyze_sales_parallel(session)
    # pprint(data_sale)
    sales_data = {}
    data_last_time = {}
    for k, v in data_sale.items():
        plan = get_plan(k)
        # pprint(plan)
        if v >= plan.sum:
            symbol = "✅"
        else:
            symbol = "🔴"

        shop = Shop.objects(uuid__exact=k).only("name").first()

        # Формирование информации о планах и фактических продажах
        data_resul[
            "{}{}".format(symbol, shop.name[:9]).upper()
        ] = "пл.{}₽/пр.{}₽".format(plan.sum, v)

        sales_data[shop.name] = v
        time_sync = TimeSync.objects(shop=k).only("time").first()
        if time_sync:
            data_last_time.update({f"🕰️ выг. {shop.name}": time_sync.time})
        else:
            data_last_time.update({f"🕰️ выг. {shop.name}": "No data"})
    # Извлекаем названия магазина и суммы продаж
    shop_names = list(sales_data.keys())
    sum_sales_ = list(sales_data.values())

    # Создаем фигуру для круговой диаграммы
    fig = px.pie(
        names=shop_names,
        values=sum_sales_,
        title="Доля выручки по Электронкам  по магазинам",
        labels={"names": "Магазины", "values": "Выручка"},
        # Цвет фона графика
    )

    # Настройки внешнего вида графика
    fig.update_layout(
        title="Продажи  по Электронкам по магазинам",
        font=dict(size=18, family="Arial, sans-serif", color="black"),
        # plot_bgcolor="black",  # Цвет фона графика
    )

    # Сохраняем диаграмму в формате PNG в объект BytesIO
    image_buffer = BytesIO()

    fig.write_image(image_buffer, format="png", width=700, height=700)

    # Очищаем буфер изображения и перемещаем указатель в начало
    image_buffer.seek(0)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения функции sync_evo: {execution_time:.2f} секунд")

    return [data_resul, data_last_time], image_buffer
