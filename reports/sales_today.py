from bd.model import Shop, Products, Documents, Session, Employees, Document, TimeSync
from .util import get_shops_uuid_user_id, last_time, sales_parallel
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

    # Получение информации о магазинах
    shops_id = get_shops_uuid_user_id(session)

    payment_type = {
        "CARD": "Банковской картой:",
        "ADVANCE": "Предоплатой (зачетом аванса):",
        "CASH": "Нал. средствами:",
        "COUNTEROFFER": "Встречным предоставлением:",
        "CREDIT": "Постоплатой (в кредит):",
        "ELECTRON": "Безналичными средствами:",
        "UNKNOWN": "Неизвестно. По-умолчанию:",
    }

    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().replace(hour=23, minute=00).isoformat()

    total_results_shops = {}
    total_result_data_payments = {}
    result_data = []
    data_last_time = {}
    # pprint(sales_parallel(shops_id, since, until).items())
    for uuid, payments in sales_parallel(shops_id, since, until).items():
        shop_name = Shop.objects(uuid__exact=uuid).only("name").first().name
        time_sync = TimeSync.objects(shop=uuid).only("time").first()
        if time_sync:
            data_last_time.update({f"🕰️ выг. {shop_name}": time_sync.time})
        else:
            data_last_time.update({f"🕰️ выг. {shop_name}": "No data"})

        sales = {"Магазин:": shop_name}

        if payments:
            sum_sales = 0
            for k, v in payments.items():
                sales[payment_type[k]] = f"{v} ₽"
                if payment_type[k] in total_result_data_payments:
                    total_result_data_payments[payment_type[k]] += v
                else:
                    total_result_data_payments[payment_type[k]] = v
                sum_sales += v
            sales["Сумма:"] = f"{sum_sales} ₽"
            result_data.append(sales)
            total_results_shops.update({shop_name: sum_sales})
    total_result_data_s = {
        "Начало периода:".upper(): since[0:10],
        "Окончание периода:".upper(): until[0:10],
    }

    total_result_data_s.update(total_result_data_payments)

    total_sum = sum(total_result_data_payments.values())

    total_result_data_s.update(
        {
            "Итого:".upper(): f"{total_sum} ₽",
        }
    )

    result_data.append(total_result_data_s)
    # pprint(total_result_data_payments)
    # pprint(total_results_shops)

    # Извлекаем названия магазина и суммы продаж
    payments_names = list(total_result_data_payments.keys())
    sum_payments = list(total_result_data_payments.values())

    # Создание круговой диаграммы для общих продаж по магазинам
    fig = px.pie(
        names=list(total_results_shops.keys()),  # Названия магазинов для внешнего круга
        values=list(total_results_shops.values()),  # Общие продажи по каждому магазину
        title="Общие продажи по магазинам",  # Заголовок внешнего круга
        labels={"names": "Магазины", "values": "Общие продажи"},  # Метки осей
    )

    # Создаем внутренний круг с данными о доле выручки по магазинам
    inner_trace = px.pie(
        names=payments_names,  # Названия магазинов для внутреннего круга
        values=sum_payments,  # Выручка по каждому магазину
        hole=0.9,  # Размер внутреннего круга
        title="Доля выручки по магазинам",  # Заголовок внутреннего круга
        labels={"names": "Магазины", "values": "Выручка"},  # Метки осей
    ).update_traces(
        hoverinfo="label+value+percent",  # Информация при наведении
        textinfo="percent",  # Информация внутри секторов
        textposition="inside",  # Позиция текста внутри секторов
        insidetextfont=dict(
            family="Arial", size=18, color="black"
        ),  # Шрифт внутри секторов
        outsidetextfont=dict(
            family="Arial", size=18, color="darkgrey"
        ),  # Шрифт снаружи секторов
        marker=dict(
            line=dict(color="white", width=1)
        ),  # Цвет и толщина линии вокруг секторов
    )

    fig.add_trace(inner_trace["data"][0])  # Добавляем внутренний круг как трассировку

    # Настройки внешнего вида графика
    fig.update_layout(
        title="<b>Продажи по магазинам<b>",  # Заголовок диаграммы (жирный текст)
        font=dict(
            size=18, family="Arial, sans-serif", color="black"
        ),  # Шрифт и его параметры
        showlegend=True,  # Показывать легенду
    )

    # Сохраняем диаграмму в формате PNG в объект BytesIO
    image_buffer = BytesIO()
    fig.write_image(image_buffer, format="png", width=900, height=900)

    # Очищаем буфер изображения и перемещаем указатель в начало
    image_buffer.seek(0)

    result_data.append(data_last_time)
    return result_data, image_buffer

    # # Типы транзакций
    # x_type = ["CLOSE_SESSION", "PAYBACK"]

    # # Создаем словарь для хранения данных о продажах
    # sales_data = {}
    # dict_last_time = {}
    # for shop_id in shops_id:
    #     dict_last_time.update(last_time(shop_id))
    #     sum_sales = 0
    #     # Получаем названия магазина shop.name
    #     shop = Shop.objects(uuid=shop_id).only("name").first()

    #     documents_sales: Document = Documents.objects(
    #         __raw__={
    #             "closeDate": {"$gte": since, "$lt": until},
    #             "shop_id": shop_id,
    #             "x_type": "SELL",
    #         }
    #     )

    #     # Итерируемся по продажам
    #     for doc in documents_sales:
    #         sum_sales += float(doc["closeResultSum"])

    #         # Добавляем данные о продажах в словарь результатов
    #     if sum_sales > 0:
    #         sales_data.update({f"{shop.name}".upper(): sum_sales})

    # report_data = {
    #     "Начало периода:".upper(): since[0:10],
    #     "Окончание периода:".upper(): until[0:10],
    # }
    # for k, v in sales_data.items():
    #     report_data.update({k: f"{v}₽"})

    # # Извлекаем названия магазина и суммы продаж
    # shop_names = list(sales_data.keys())
    # sum_sales_ = list(sales_data.values())
    # # Создаем фигуру для круговой диаграммы
    # fig = px.pie(
    #     names=shop_names,
    #     values=sum_sales_,
    #     title="Доля выручки по магазинам",
    #     labels={"names": "Магазины", "values": "Выручка"},
    #     # Цвет фона графика
    # )

    # # Настройки внешнего вида графика
    # fig.update_layout(
    #     title="Продажи по магазинам",
    #     font=dict(size=18, family="Arial, sans-serif", color="black"),
    #     # plot_bgcolor="black",  # Цвет фона графика
    # )

    # # Сохраняем диаграмму в формате PNG в объект BytesIO
    # image_buffer = BytesIO()

    # fig.write_image(image_buffer, format="png", width=900, height=900)

    # # Очищаем буфер изображения и перемещаем указатель в начало
    # image_buffer.seek(0)

    # # Рассчитываем сумму всех продаж
    # total_sales = sum(sum_sales_)

    # # Обновляем данные отчета
    # report_data.update({"Итого выручка:".upper(): f"{total_sales}₽"})

    # # last_time = (
    # #     Documents.objects(
    # #         __raw__={
    # #             "closeDate": {"$gte": since, "$lt": until},
    # #         }
    # #     )
    # #     .order_by("-closeDate")
    # #     .only("closeDate")
    # #     .first()
    # # )
    # # if last_time:
    # #     time = get(last_time.closeDate).shift(hours=3).isoformat()[11:19]
    # # else:
    # #     time = 0

    # # report_data.update(
    # #     {
    # #         "🕰️ Время выгрузки ->".upper(): time,
    # #     }
    # # )

    # # plt.close()
    # return [report_data, dict_last_time], image_buffer
