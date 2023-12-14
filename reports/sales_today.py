from bd.model import Shop, Products, Documents, Session, Employees
from .util import (
    get_shops_uuid_user_id,
)
from pprint import pprint
from arrow import get, utcnow
import plotly.express as px
from io import BytesIO


name = "🧾 🛒 продажи сегодня➡️".upper()
desc = ""
mime = "image_bytes"


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    shops_id_2 = {
        "20220202-B042-4021-803D-09E15DADE8A4": "20220430-A472-40B8-8077-2EE96318B7E7",
        "20220201-19C9-40B0-8082-DF8A9067705D": "20220501-9ADF-402C-8012-FB88547F6222",
        # '20220202-B042-4021-803D-09E15DADE8A4': '20220501-CB2E-4020-808C-E3FD3CB1A1D4',
        "20210712-1362-4012-8026-5A35685630B2": "20220501-DDCF-409A-8022-486441F27458",
        "20220201-8B00-40C2-8002-EF7E53ED1220": "20220501-3254-40E5-809E-AC6BB204D373",
        "20220201-A55A-40B8-8071-EC8733AFFA8E": "20220501-4D25-40AD-80DA-77FAE02A007E",
        # "20220202-B042-4021-803D-09E15DADE8A4": "20230214-33E5-4085-80A3-28C177E34112",
    }

    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().replace(hour=23, minute=00).isoformat()

    # Получение информации о магазинах
    shops_id = get_shops_uuid_user_id(session)

    # Типы транзакций
    x_type = ["CLOSE_SESSION", "PAYBACK"]

    # Создаем словарь для хранения данных о продажах
    sales_data = {}

    for shop_id in shops_id:
        sum_sales = 0
        # Получаем названия магазина shop.name
        shop = Shop.objects(uuid=shop_id).only("name").first()
        if shop_id in shops_id_2:
            new_shops_id = [shop_id, shops_id_2[shop_id]]
        else:
            new_shops_id = [shop_id]

        documents_sales = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": {"$in": new_shops_id},
                "x_type": "SELL",
            }
        )

        # Итерируемся по продажам
        for doc in documents_sales:
            sum_sales += float(doc["closeResultSum"])

            # Добавляем данные о продажах в словарь результатов
        if sum_sales > 0:
            sales_data.update({f"{shop.name}".upper(): sum_sales})

    report_data = {
        "Начало периода:".upper(): since[0:10],
        "Окончание периода:".upper(): until[0:10],
    }
    for k, v in sales_data.items():
        report_data.update({k: f"{v}₽"})

    # Извлекаем названия магазина и суммы продаж
    shop_names = list(sales_data.keys())
    sum_sales_ = list(sales_data.values())
    # Создаем фигуру для круговой диаграммы
    fig = px.pie(
        names=shop_names,
        values=sum_sales_,
        title="Доля выручки по магазинам",
        labels={"names": "Магазины", "values": "Выручка"},
        # Цвет фона графика
    )

    # Настройки внешнего вида графика
    fig.update_layout(
        title="Продажи по магазинам",
        font=dict(size=18, family="Arial, sans-serif", color="black"),
        # plot_bgcolor="black",  # Цвет фона графика
    )

    # Сохраняем диаграмму в формате PNG в объект BytesIO
    image_buffer = BytesIO()

    fig.write_image(image_buffer, format="png", width=900, height=900)

    # Очищаем буфер изображения и перемещаем указатель в начало
    image_buffer.seek(0)

    # Рассчитываем сумму всех продаж
    total_sales = sum(sum_sales_)

    # Обновляем данные отчета
    report_data.update({"Итого выручка:".upper(): f"{total_sales}₽"})

    # plt.close()
    return [report_data], image_buffer
