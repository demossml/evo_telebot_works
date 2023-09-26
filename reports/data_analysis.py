from bd.model import Shop, Products, Documents, Session, Employees, Shift_Opening_Report
from .util import (
    get_intervals,
    get_period,
    get_period_,
    get_period_day,
    get_shops_user_id,
    get_shops,
    get_shops_last_room,
)
from pprint import pprint
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from arrow import get, utcnow
import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO


from .inputs import (
    ReportDataAnalysisInput,
    ShopAllInput,
    GroupInput,
    GroupsInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
    DocStatusInput,
)


name = "📉📈📊 АНАЛИЗ ДАННЫХ➡️"
desc = ""
mime = "image_bytes"


def get_inputs(session: Session):
    period = ["day", "week", "fortnight", "month"]
    if session.params["inputs"]["0"]:
        if "period" in session.params["inputs"]["0"]:
            if session.params["inputs"]["0"]["period"] == "day":
                return {}
            if session.params["inputs"]["0"]["period"] not in period:
                return {"openDate": OpenDatePastInput}
            else:
                if (
                    session.params["inputs"]["0"]["report"]
                    == "analysis_sales_by_day_the_week"
                ):
                    return {"openDate": OpenDatePastInput}
                else:
                    return {
                        "openDate": OpenDatePastInput,
                        "closeDate": CloseDatePastInput,
                    }
        if session.params["inputs"]["0"]["report"] == "analysis_sales_shops":
            return {
                "period": PeriodDateInput,
            }
        if session.params["inputs"]["0"]["report"] == "analysis_outcome_shops":
            return {
                "period": PeriodDateInput,
            }
        if session.params["inputs"]["0"]["report"] == "analysis_sales_shops_group":
            return {
                "group": GroupInput,
                "period": PeriodDateInput,
            }
        if session.params["inputs"]["0"]["report"] == "analysis_sales_shops_groups":
            if "shop" in session.params["inputs"]["0"]:
                return {
                    "parentUuid": GroupsInput,
                    "docStatus": DocStatusInput,
                    "period": PeriodDateInput,
                }
            else:
                return {
                    "shop": ShopAllInput,
                }
        if session.params["inputs"]["0"]["report"] == "analysis_sales_by_day_the_week":
            return {
                "shop": ShopAllInput,
                "period": PeriodDateInput,
            }
    else:
        return {"report": ReportDataAnalysisInput}


def generate(session: Session):
    # Получение параметров из сессии
    params = session.params["inputs"]["0"]
    room = session["room"]

    shops_id_2 = {
        "20200630-3E0D-4061-80C1-F7897E112F00": "20220430-A472-40B8-8077-2EE96318B7E7",
        "20220201-19C9-40B0-8082-DF8A9067705D": "20220501-9ADF-402C-8012-FB88547F6222",
        "20220222-6C28-4069-8006-082BE12BEB32": "20220601-4E97-40A5-801B-1A29127AFA8B",
        "20210923-FB1F-4023-80F6-9ECB3F5A0FA8": "20220501-11CA-40E0-8031-49EADC90D1C4",
        # '20220202-B042-4021-803D-09E15DADE8A4': '20220501-CB2E-4020-808C-E3FD3CB1A1D4',
        "20210712-1362-4012-8026-5A35685630B2": "20220501-DDCF-409A-8022-486441F27458",
        "20220201-8B00-40C2-8002-EF7E53ED1220": "20220501-3254-40E5-809E-AC6BB204D373",
        "20220201-A55A-40B8-8071-EC8733AFFA8E": "20220501-4D25-40AD-80DA-77FAE02A007E",
        "20220202-B042-4021-803D-09E15DADE8A4": "20230214-33E5-4085-80A3-28C177E34112",
    }
    if params["report"] == "analysis_sales_shops":
        period = get_period(session)
        since = period["since"]
        until = period["until"]

        # Получение информации о магазинах
        shops = get_shops(session)
        shops_id = shops["shop_id"]

        # Типы транзакций
        x_type = ["CLOSE_SESSION", "PAYBACK"]

        # Создаем словарь для хранения данных о продажах
        sales_data = {}

        # Итерируемся по uuid магазинов
        for shop_id in shops_id:
            sum_sales = 0
            # Получаем названия магазина shop.name
            shop = Shop.objects(uuid=shop_id).only("name").first()
            if shop_id in shops_id_2:
                new_shops_id = [shop_id, shops_id_2[shop_id]]
            else:
                new_shops_id = [shop_id]
            for new_shop_id in new_shops_id:
                # Получаем документы о  закрытии дня
                documents_close_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": new_shop_id,
                        "x_type": "CLOSE_SESSION",
                    }
                )
                # Если есть информация о закрытии дня
                if len(documents_close_session) > 0:
                    for document_close_session in documents_close_session:
                        sum_sales += float(document_close_session["closeResultSum"])

                else:
                    #  Получаем документы о продажах
                    documents_sales = Documents.objects(
                        __raw__={
                            "closeDate": {"$gte": since, "$lt": until},
                            "shop_id": new_shop_id,
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

        fig.write_image(image_buffer, format="png", width=700, height=700)

        # Очищаем буфер изображения и перемещаем указатель в начало
        image_buffer.seek(0)

        # Рассчитываем сумму всех продаж
        total_sales = sum(sum_sales_)

        # Обновляем данные отчета
        report_data.update({"Итого выручка:".upper(): f"{total_sales}₽"})

        return [report_data], image_buffer
    if params["report"] == "analysis_outcome_shops":
        period = get_period(session)
        since = period["since"]
        until = period["until"]

        # Получение информации о магазинах
        shops = get_shops(session)
        shops_id = shops["shop_id"]

        # Типы транзакций
        x_type = ["CLOSE_SESSION", "PAYBACK"]

        # Создаем словарь для хранения данных о продажах
        sales_data = {}

        # Итерируемся по uuid магазинов
        for shop_id in shops_id:
            sum_sales = 0
            # Получаем названия магазина shop.name
            shop = Shop.objects(uuid=shop_id).only("name").first()
            if shop_id in shops_id_2:
                new_shops_id = [shop_id, shops_id_2[shop_id]]
            else:
                new_shops_id = [shop_id]
            for new_shop_id in new_shops_id:
                # Получаем документы о  закрытии дня
                documents_payback = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": new_shop_id,
                        "x_type": "PAYBACK",
                    }
                )
                # Если есть информация о закрытии дня
                if len(documents_payback) > 0:
                    for document_payback in documents_payback:
                        sum_sales += float(document_payback["closeResultSum"])

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
            title="Возвраты по магазинам",
            font=dict(size=18, family="Arial, sans-serif", color="black"),
            # plot_bgcolor="black",  # Цвет фона графика
        )

        # Сохраняем диаграмму в формате PNG в объект BytesIO
        image_buffer = BytesIO()

        fig.write_image(image_buffer, format="png", width=700, height=700)

        # Очищаем буфер изображения и перемещаем указатель в начало
        image_buffer.seek(0)

        # Рассчитываем сумму всех продаж
        total_sales = sum(sum_sales_)

        # Обновляем данные отчета
        report_data.update({"Итого возвратов:".upper(): f"{total_sales}₽"})

        return [report_data], image_buffer
    if params["report"] == "analysis_sales_shops_group":
        period = get_period(session)
        since = period["since"]
        until = period["until"]

        parentUuid = session.params["inputs"]["0"]["group"]
        group = Products.objects(group=True, uuid=parentUuid).only("name").first()
        products_uuid = [
            i.uuid for i in Products.objects(group=False, parentUuid=parentUuid)
        ]

        # Получение информации о магазинах
        shops = get_shops(session)
        shops_id = shops["shop_id"]

        # Типы транзакций
        x_type = ["SELL", "PAYBACK"]

        # Создаем словарь для хранения данных о продажах
        sales_data = {}

        # Итерируемся по uuid магазинов
        for shop_id in shops_id:
            sum_sales = 0
            # Получаем названия магазина shop.name
            shop = Shop.objects(uuid=shop_id).only("name").first()

            # Фильтруем документы в базе данных MongoDB
            documents_sales = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop_id,
                    "x_type": {"$in": x_type},
                    "transactions.commodityUuid": {"$in": products_uuid},
                }
            )

            # Обработка документов
            for doc in documents_sales:
                for trans in doc["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        if trans["commodityUuid"] in products_uuid:
                            sum_sales += trans["sum"]

            if sum_sales > 0:
                sales_data.update({f"{shop.name}".upper(): sum_sales})

        report_data = {
            "ГРУППА:": group.name,
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
            title=f"Доля выручки по {group.name} по магазинам",
            labels={"names": "Магазины", "values": "Выручка"},
            # Цвет фона графика
        )

        # Настройки внешнего вида графика
        fig.update_layout(
            title=f"Продажи по {group.name} по магазинам",
            font=dict(size=18, family="Arial, sans-serif", color="black"),
            # plot_bgcolor="black",  # Цвет фона графика
        )

        # Сохраняем диаграмму в формате PNG в объект BytesIO
        image_buffer = BytesIO()

        fig.write_image(image_buffer, format="png", width=800, height=800)

        # Очищаем буфер изображения и перемещаем указатель в начало
        image_buffer.seek(0)

        # Рассчитываем сумму всех продаж
        total_sales = sum(sum_sales_)

        # Обновляем данные отчета
        report_data.update({"Итого выручка:".upper(): f"{total_sales}₽"})

        return [report_data], image_buffer
    if params["report"] == "analysis_sales_shops_groups":
        period = get_period_(session)
        pprint(period)
        since = period["since"]
        until = period["until"]

        # Получение информации о магазинах
        shops = get_shops(session)
        shops_id = shops["shop_id"]
        shops_name = shops["shop_name"]

        parentUuids = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            # если в 'uuid' есть в session.params["inputs"][str(i)]
            if "parentUuid" in session.params["inputs"][str(i)]:
                # если 'uuid' нет в словаре с ключем i в списке uuid
                parentUuids.append(session.params["inputs"][str(i)]["parentUuid"])
        # pprint(parentUuids)
        # Создаем словарь для хранения данных о продажах

        sales_data = {}

        for parentUuid in parentUuids:
            pprint(parentUuid)
            group = Products.objects(group=True, uuid=parentUuid).only("name").first()

            products_uuid_ = []

            for i in Products.objects(parentUuid=parentUuid):
                if i["uuid"] not in products_uuid_:
                    products_uuid_.append(i["uuid"])

            # Типы транзакций
            x_type = ["SELL", "PAYBACK"]

            sum_sales = 0

            # Фильтруем документы в базе данных MongoDB
            documents_sales = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": {"$in": shops_id},
                    "x_type": {"$in": x_type},
                    "transactions.commodityUuid": {"$in": products_uuid_},
                }
            )

            # pprint(documents_sales)

            # Обработка документов
            for doc in documents_sales:
                for trans in doc["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        if trans["commodityUuid"] in products_uuid_:
                            sum_sales += trans["sum"]

            if sum_sales > 0:
                sales_data.update({f"{group.name}".upper(): sum_sales})

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
            title=f"Доля выручки группам  по магазинам",
            labels={"names": "Магазины", "values": "Выручка"},
            # Цвет фона графика
        )

        # Настройки внешнего вида графика
        fig.update_layout(
            title=f"Продажи по магазин(ы) {shops_name}".upper(),
            font=dict(size=18, family="Arial, sans-serif", color="black"),
            # plot_bgcolor="black",  # Цвет фона графика
        )

        # Сохраняем диаграмму в формате PNG в объект BytesIO
        image_buffer = BytesIO()

        fig.write_image(image_buffer, format="png", width=800, height=800)

        # Очищаем буфер изображения и перемещаем указатель в начало
        image_buffer.seek(0)

        # Рассчитываем сумму всех продаж
        total_sales = sum(sum_sales_)

        # Обновляем данные отчета
        report_data.update({"Итого выручка:".upper(): f"{total_sales}₽"})

        return [report_data], image_buffer
    if params["report"] == "analysis_sales_by_day_the_week":
        params = session.params["inputs"]["0"]

        # Получение информации о магазинах
        shops = get_shops(session)
        shops_id = shops["shop_id"]
        shops_name = shops["shop_name"]

        period = get_period_day(session)
        since = period["since"]
        until = period["until"]

        documents_break_report = Shift_Opening_Report.objects(
            __raw__={
                "openData": {"$gte": since, "$lt": until},
                "x_type": "BREAK",
                # "break": "open",
                "shop_id": {"$in": shops_id},
            }
        )

        beginning_of_period = []
        end_of_period = []
        if len(documents_break_report) > 0:
            for doc_break in documents_break_report:
                beginning_of_period.append(doc_break["openData"][11:16])
                if "closeDate" in doc_break:
                    end_of_period.append(doc_break["closeDate"][11:16])
        pprint(beginning_of_period)
        pprint(end_of_period)

        end_date = get(since).shift(days=-7).isoformat()

        # Преобразуем начальную дату в строку в формате ISO с временем 00:00
        since2 = get(end_date).replace(hour=0, minute=0).isoformat()

        # Преобразуем конечную дату в строку в формате ISO с временем 23:59
        until2 = get(end_date).replace(hour=23, minute=59).isoformat()

        data_t = [{"since": since, "until": until}, {"since": since2, "until": until2}]
        pprint(data_t)

        total_sales_data = []
        for i in data_t:
            pprint(i["since"])
            sales_data = {}
            for since3, until3 in get_intervals(i["since"], i["until"], "minutes", 30):
                sales_sum = 0
                documents = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since3, "$lt": until3},
                        "shop_id": {"$in": shops_id},
                        "x_type": "SELL",
                        # 'transactions.commodityUuid': {'$in': products_uuid}
                    }
                )
                for i2 in documents:
                    sales_sum = +int(float(i2["closeResultSum"]))
                if sales_sum > 0:
                    sales_data.update(
                        {get(until3).shift(hours=3).isoformat()[11:16]: sales_sum}
                    )
            total_sales_data.append(sales_data)
        # pprint(total_sales_data)

        # Создаем списки для времени и продаж для каждого дня
        time = list(total_sales_data[0].keys())
        day1_sales = list(total_sales_data[0].values())
        day2_sales = list(total_sales_data[1].values())

        # Вычисляем разницу между продажами первого и второго дня
        sales_difference = [day1 - day2 for day1, day2, in zip(day1_sales, day2_sales)]

        # Создаем графики для каждого дня
        fig = go.Figure()

        # Добавляем столбцы для первого дня
        fig.add_trace(
            go.Bar(
                x=time,
                y=day2_sales,
                name=f"{since3[:10]}",
                text=day2_sales,  # Сумма продаж на вершинах
                opacity=0.7,  # Прозрачность полосы
            )
        )

        # Добавляем столбцы для второго дня с наложением на первый день
        fig.add_trace(
            go.Bar(
                x=time,
                y=day1_sales,
                name=f"{since[:10]}",
                text=day1_sales,  # Сумма продаж на вершинах
                opacity=0.7,  # Прозрачность полосы
            )
        )

        # Добавляем аннотации с отрицательной разницей продаж
        for i, diff in enumerate(sales_difference):
            # if diff < 0:
            fig.add_annotation(
                x=time[i],
                y=max(day1_sales[i], day2_sales[i]),
                text=f"{diff}",
                showarrow=True,
                arrowhead=1,
                arrowwidth=2,
                ay=-50,  # Длина стрелки (смещение по вертикали)
                arrowcolor="yellow",
                font=dict(color="black", size=12),  # Цвет и размер текста аннотации
                align="center",
                yanchor="top",
            )

        # Добавляем красные полосы (маркеры) на график по оси X

        fig.update_layout(
            barmode="overlay",  # Наложение столбцов
            xaxis_title="Интервал (по 30 минутам)",  # Заголовок оси X
            yaxis_title="Продажи ₽",  # Заголовок оси Y
            title=f"Сравнение двух дней продаж по магазину(ы) {shops_name}",  # Заголовок графика
            plot_bgcolor="lightgray",  # Цвет фона графика
        )

        # Создаем график для второй оси X
        fig2 = go.Figure()

        # Добавляем красные полосы (маркеры) на график по второй оси X
        for begin, end in zip(beginning_of_period, end_of_period):
            fig2.add_trace(
                go.Scatter(
                    x=[begin, end],
                    y=[0, 0],
                    mode="markers",
                    marker=dict(color="red", size=10),
                    showlegend=False,  # Не отображать в легенде
                )
            )

        # Настройка макета для второй оси X
        fig2.update_layout(
            xaxis=dict(
                domain=[0, 1],  # Позиция второй оси X (полностью под основной осью X)
                # showticklabels=False,  # Не показывать метки на второй оси X
                # showgrid=False,  # Не показывать сетку на второй оси X
            ),
            #     yaxis=dict(
            #         showticklabels=False,  # Не показывать метки на оси Y второй оси X
            #     ),
        )

        # Объединяем основной график и график второй оси X
        fig.add_traces(fig2.data)

        # Отображаем график
        fig.show()

        # Сохраняем график в формате PNG
        image_buffer = BytesIO()
        pio.write_image(fig, image_buffer, format="png", width=1200, height=900)

        # Очищаем буфер изображения и перемещаем указатель в начало
        image_buffer.seek(0)

        # with open("sales_comparison.jpg", "wb") as f:
        #     f.write(image_buffer.read())
        return [{"": ""}], image_buffer
