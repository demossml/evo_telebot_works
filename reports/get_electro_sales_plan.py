# Получить план продажи по группе товаров по всем магазинам в руб.
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id, id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from bd.model import Session, Shop, Products, Documents, Employees, Message, Plan
from arrow import utcnow, get
from pprint import pprint
from .util import get_shops, get_shops_in, generate_plan
import telebot
import plotly.express as px
from io import BytesIO

name = "💹 План по Электронкам ➡️".upper()
desc = "Генерирует отчет по продажам в шт. по одной группе товаров в одном магазине за фиксированный период"
mime = "image_bytes"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    # Группы товаров для анализа продаж
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

    # Определение временного периода для анализа
    since_2 = utcnow().replace(hour=3, minute=00).isoformat()
    until_2 = utcnow().isoformat()

    # Заранее определенные идентификаторы магазинов
    _in = [
        "20190411-5A3A-40AC-80B3-8B405633C8BA",
        "20190327-A48C-407F-801F-DA33CB4FBBE9",
        "20191117-BF71-40FE-8016-1E7E4A3A4780",
        "20210712-1362-4012-8026-5A35685630B2",
        # "20220222-6C28-4069-8006-082BE12BEB32",
        "20200630-3E0D-4061-80C1-F7897E112F00",
        "20210923-FB1F-4023-80F6-9ECB3F5A0FA8",
        "20220201-19C9-40B0-8082-DF8A9067705D",
        "20220201-8B00-40C2-8002-EF7E53ED1220",
        "20220201-A55A-40B8-8071-EC8733AFFA8E",
        "20220202-B042-4021-803D-09E15DADE8A4",
        "20231001-6611-407F-8068-AC44283C9196",
    ]
    uuid = [
        "20210712-1362-4012-8026-5A35685630B2",
        "20190411-5A3A-40AC-80B3-8B405633C8BA",
        "20190327-A48C-407F-801F-DA33CB4FBBE9",
        "20191117-BF71-40FE-8016-1E7E4A3A4780",
        # "20220222-6C28-4069-8006-082BE12BEB32",
        "20200630-3E0D-4061-80C1-F7897E112F00",
        # "20210923-FB1F-4023-80F6-9ECB3F5A0FA8",
        "20220201-19C9-40B0-8082-DF8A9067705D",
        "20220201-8B00-40C2-8002-EF7E53ED1220",
        "20220201-A55A-40B8-8071-EC8733AFFA8E",
        "20220202-B042-4021-803D-09E15DADE8A4",
        "20231001-6611-407F-8068-AC44283C9196",
    ]

    # Получение информации о магазинах на основе заранее определенных идентификаторов
    shops_uuid = [i.uuid for i in get_shops_in(session, _in)]

    _dict_2 = {}
    # Словарь для хранения данных о продажах по магазинам
    sales_data = {}

    for shop in Shop.objects(uuid__in=uuid):
        since = utcnow().replace(hour=3, minute=00).isoformat()
        until = utcnow().replace(hour=20, minute=59).isoformat()

        # Получение данных о планах продаж для магазина
        plan_ = Plan.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": shop["uuid"],
            }
        )
        if len(plan_) > 0:
            # pprint(1)
            plan = Plan.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop["uuid"],
                }
            ).first()
        else:
            # Если планы отсутствуют, генерируем их
            generate_plan()
            # pprint(2)
            plan = Plan.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop["uuid"],
                }
            ).first()

        # Получение списка продуктов, относящихся к группам товаров
        products = Products.objects(
            __raw__={"shop_id": shop["uuid"], "parentUuid": {"$in": group_id}}
        )

        # Формирование списка идентификаторов продуктов
        products_uuid = [element.uuid for element in products]

        # Типы операций для анализа (продажи и возвраты)
        x_type = ["SELL", "PAYBACK"]

        # Получение документов о продажах и возвратах для продуктов
        documents_2 = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since_2, "$lt": until_2},
                "shop_id": shop["uuid"],
                "x_type": {"$in": x_type},
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )

        sum_sell_today = 0
        # Вычисление суммы продаж за текущий период
        for doc_2 in documents_2:
            for trans_2 in doc_2["transactions"]:
                if trans_2["x_type"] == "REGISTER_POSITION":
                    if trans_2["commodityUuid"] in products_uuid:
                        sum_sell_today += trans_2["sum"]

        if sum_sell_today > 0:
            sales_data.update({shop["name"]: sum_sell_today})

        pprint(sales_data)

        # Добавление данных о продажах для текущего магазина
        if int(sum_sell_today) >= int(plan.sum):
            symbol = "✅"
        else:
            symbol = "🔴"

        # Формирование информации о планах и фактических продажах
        if shop["uuid"] in shops_uuid:
            _dict_2[
                "{}{}".format(symbol, shop["name"][:9]).upper()
            ] = "пл.{}₽/пр.{}₽".format(int(plan.sum), int(sum_sell_today))

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

    return [_dict_2], image_buffer

    # return [_dict_2]
