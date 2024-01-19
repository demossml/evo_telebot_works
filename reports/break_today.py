from arrow import utcnow, get
from bd.model import (
    Session,
    Shift_Opening_Report,
)
from .util import get_shops_user_id

from pprint import pprint
import plotly.express as px
from io import BytesIO

name = "🕒️🚬🌯перерывы сегодня ➡️".upper()
desc = "Собирает данные о перерывах"
mime = "image_bytes"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    result = []

    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().replace(hour=20, minute=59).isoformat()

    shops = get_shops_user_id(session)

    break_data = {}

    for shop in shops:
        documents_break_report = Shift_Opening_Report.objects(
            __raw__={
                "openData": {"$gte": since, "$lt": until},
                "x_type": "BREAK",
                "shop_id": shop["uuid"],
            }
        )

        total_delta = 0

        if len(documents_break_report) > 0:
            for doc in documents_break_report:
                if "closeDate" in doc:
                    delta = (
                        (get(doc["closeDate"]) - get(doc["openData"])).seconds
                        // 60
                        % 60
                    )
                    total_delta += delta
        if total_delta > 0:
            break_data.update({shop["name"]: total_delta})
    break_result = {}
    for k, v in break_data.items():
        break_result.update(
            {
                k: f"{v} минут",
            }
        )
    pprint(break_result)

    # Извлекаем названия магазина и суммы продаж
    shop_names = list(break_data.keys())
    delta_ = list(break_data.values())

    # Создаем фигуру для круговой диаграммы
    fig = px.pie(
        names=shop_names,
        values=delta_,
        title="Доля времяни перерыва по магазинам",
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

    fig.write_image(image_buffer, format="png", width=800, height=800)

    # Очищаем буфер изображения и перемещаем указатель в начало
    image_buffer.seek(0)

    return [break_result], image_buffer
