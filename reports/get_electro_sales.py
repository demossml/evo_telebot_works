# Получить продажи по группе товаров по одному магазину в штуках по наименованию
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id,  id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from bd.model import Session, Shop, Products, Documents
from arrow import utcnow, get
from pprint import pprint
from .util import get_shops_user_id
from collections import OrderedDict
from io import BytesIO
import plotly.express as px


name = " 💨💨💨 Fyzzi/Электро ➡️".upper()
desc = "Генерирует отчет по продажам в шт. по электронкам в шт"
mime = "image_bytes"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    shops = get_shops_user_id(session)
    # shops_id = [v.uuid for v in shops]
    # pprint(shops_id)
    group_id = (
        "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
        "568905bd-9460-11ee-9ef4-be8fe126e7b9",
        "2b8eb6b4-92ea-11ee-ab93-2cf05d04be1d",
        "568905be-9460-11ee-9ef4-be8fe126e7b9",
        "ad8afa41-737d-11ea-b9b9-70c94e4ebe6a",
        "8a8fcb5f-9582-11ee-ab93-2cf05d04be1d",
        "78ddfd78-dc52-11e8-b970-ccb0da458b5a",
    )

    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().isoformat()

    result = []
    _dict = {}
    for shop in shops:
        products = Products.objects(
            __raw__={"parentUuid": {"$in": group_id}, "shop_id": shop["uuid"]}
        ).only("uuid")

        products_uuid = [element.uuid for element in products]
        result_shop = {}
        shop_ = Shop.objects(uuid=shop["uuid"]).only("name").first()
        shop_name = shop_.name
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

    # Извлекаем названия магазина и суммы продаж
    products_names = list(_dict.keys())
    sum_sales_quantity = list(_dict.values())

    # Создаем фигуру для круговой диаграммы
    fig = px.pie(
        names=products_names,
        values=sum_sales_quantity,
        title="Доля выручки по Электронкам  по магазинам в шт.",
        labels={"names": "Продукт", "values": "количество"},
        # Цвет фона графика
    ).update_traces(
        # Шаблон текста внутри каждого сектора
        # %{label}: подставляет название категории
        # %{value:$,s}: подставляет значение с форматированием в долларах и использованием запятых
        # <br>: добавляет перенос строки (HTML тег)
        # %{percent}: подставляет процентное соотношение
        texttemplate="%{label}: <br>%{percent}",
        showlegend=False,  # Устанавливаем showlegend в False, чтобы скрыть легенду
    )

    # Настройки внешнего вида графика
    fig.update_layout(
        title="Продажи  по Электронкам по магазинам в шт.",
        font=dict(size=18, family="Arial, sans-serif", color="black"),
        # plot_bgcolor="black",  # Цвет фона графика
    )

    # Сохраняем диаграмму в формате PNG в объект BytesIO
    image_buffer = BytesIO()

    fig.write_image(image_buffer, format="png", width=900, height=900)

    # Очищаем буфер изображения и перемещаем указатель в начало
    image_buffer.seek(0)

    return result, image_buffer
