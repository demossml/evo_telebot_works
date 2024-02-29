# Получить продажи по группе товаров по одному магазину в штуках по наименованию
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id,  id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from bd.model import Session, Shop, Products, Documents
from arrow import utcnow, get
from pprint import pprint
from .util import get_shops_user_id, get_top_n_sales
from collections import OrderedDict
from io import BytesIO
import plotly.express as px
import io


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

    # Сортируем словарь по убыванию количества продаж
    sorted_sales = get_top_n_sales(_dict)

    if len(sorted_sales[0]) > 0:

        # Извлекаем названия магазина и суммы продаж
        shop_names = list(sorted_sales[0].keys())
        sum_sales_quantity = list(sorted_sales[0].values())
        sum_sales_quantity_total = sum(sorted_sales[0].values())

        # Создаем фигуру для гистограммы
        fig = px.bar(
            y=shop_names,
            x=sum_sales_quantity,
            title=f"Продажи в шт. . Топ {sorted_sales[1]}.Начало/Окончание периода - {since[0:10]}/{until[0:10]}",
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
        target_height = max(700, len(shop_names) * 54)

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

    return result, image_buffer
