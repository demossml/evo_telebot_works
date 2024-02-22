# Получить план продажи по группе товаров по всем магазинам в руб.
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id, id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from bd.model import Session, Shop, Plan, Products, Documents, TimeSync, Status
from pprint import pprint
from .util import (
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

    data_resul = {}
    data_sale = analyze_sales_parallel(session)
    pprint(data_sale)
    sales_data = {}
    data_last_time = {}
    for k, v in data_sale.items():
        doc_status = Status.objects(shop=k, status="deleted").first()
        if not doc_status:
            plan = get_plan(k)
            # pprint(plan)
            if v >= plan.sum:
                symbol = "✅"
            else:
                symbol = "🔴"

            shop = Shop.objects(uuid__exact=k).only("name").first()

            # Формирование информации о планах и фактических продажах
            data_resul["{}{}".format(symbol, shop.name[:9]).upper()] = (
                "пл.{}₽/пр.{}₽".format(plan.sum, v)
            )

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
