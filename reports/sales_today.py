from bd.model import Shop, Products, Documents, Session, Employees, Document
from .util import get_shops_uuid_user_id, last_time
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
    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().replace(hour=23, minute=00).isoformat()

    # Получение информации о магазинах
    shops_id = get_shops_uuid_user_id(session)

    # Типы транзакций
    x_type = ["CLOSE_SESSION", "PAYBACK"]

    # Создаем словарь для хранения данных о продажах
    sales_data = {}
    dict_last_time = {}
    for shop_id in shops_id:
        dict_last_time.update(last_time(shop_id))
        sum_sales = 0
        # Получаем названия магазина shop.name
        shop = Shop.objects(uuid=shop_id).only("name").first()

        documents_sales: Document = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": shop_id,
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

    # last_time = (
    #     Documents.objects(
    #         __raw__={
    #             "closeDate": {"$gte": since, "$lt": until},
    #         }
    #     )
    #     .order_by("-closeDate")
    #     .only("closeDate")
    #     .first()
    # )
    # if last_time:
    #     time = get(last_time.closeDate).shift(hours=3).isoformat()[11:19]
    # else:
    #     time = 0

    # report_data.update(
    #     {
    #         "🕰️ Время выгрузки ->".upper(): time,
    #     }
    # )

    # plt.close()
    return [report_data, dict_last_time], image_buffer
