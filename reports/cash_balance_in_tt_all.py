from arrow import utcnow, get
from bd.model import Session, Shop, TimeSync
from pprint import pprint
from .inputs import (
    ShopAllInput,
)
from .util import get_shops, calculate_for_shops
from decimal import Decimal
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import plotly.express as px
from io import BytesIO


name = "💰🚬 ₱ в кассах ТТ ➡️".upper()
desc = "Остаток в кассе"
mime = "image_bytes"


def get_inputs(session: Session):
    return {"shop": ShopAllInput}


def generate(session: Session):

    # Получение информации о магазинах
    shops = get_shops(session)

    # Извлечение идентификаторов магазинов из данных о магазинах
    shops_id = shops["shop_id"]

    # Вычисление данных по кассе для каждого магазина
    cash_date = calculate_for_shops(shops_id)

    # Инициализация списка для хранения результатовы
    result_date = []

    # Инициализация словаря для хранения данных по кассе для отчета
    report_date = {}

    # Инициализация словаря для хранения времени последней синхронизации данных
    data_last_time = {}

    # Обработка данных по кассе для каждого магазина
    for k, v in cash_date.items():

        # Получение имени магазина по его идентификатору
        shop_name = Shop.objects(uuid=k).only("name").first().name
        report_date.update({shop_name: v})

        # Получение времени последней синхронизации данных для магазина (если есть)
        time_sync = TimeSync.objects(shop=k).only("time").first()
        if time_sync:
            data_last_time.update({f"🕰️ выг. {shop_name}": time_sync.time})
        else:
            data_last_time.update({f"🕰️ выг. {shop_name}": "No data"})

    # Извлекаем названия магазина и суммы продаж
    shop_names = list(report_date.keys())
    sum_cash = list(report_date.values())

    # Создаем фигуру для круговой диаграммы
    fig = px.pie(
        names=shop_names,
        values=sum_cash,
        title="Доля выручки по Электронкам  по магазинам",
        labels={"names": "Магазины", "values": "Выручка"},
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
        title="Продажи  по Электронкам по магазинам",
        font=dict(size=18, family="Arial, sans-serif", color="black"),
        # plot_bgcolor="black",  # Цвет фона графика
    )

    # Сохраняем диаграмму в формате PNG в объект BytesIO
    image_buffer = BytesIO()

    fig.write_image(image_buffer, format="png", width=900, height=900)

    # Очищаем буфер изображения и перемещаем указатель в начало
    image_buffer.seek(0)

    # Обновление значений в словаре report_date с добавлением символа валюты "₱"
    updated_report_data = {k: f"{v}₱" for k, v in report_date.items()}

    # Добавление обновленных данных по кассе и времени последней синхронизации в результаты
    result_date.append(updated_report_data)
    result_date.append(data_last_time)

    return result_date, image_buffer
