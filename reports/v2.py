from bd.model import (
    Session,
    Shop,
    Products,
    Documents,
    Employees,
    Message,
    Shift_Opening_Report,
)
from arrow import utcnow, get
from pprint import pprint
from .util import get_products, period_to_date, get_intervals, get_shops, get_period

from .inputs import (
    ReportSalesInput,
    ShopAllInput,
    GroupInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
)

import plotly.express as px
from io import BytesIO

name = "Отчет ₽".upper()
desc = ""
mime = "image_bytes"


class PeriodOpenDateInput:
    name = "Магазин"
    desc = "Выберите период"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "day", "name": "День"},
            {"id": "week", "name": "Неделя"},
            {"id": "fortnight", "name": "Две недели"},
            {"id": "month", "name": "Месяц"},
        ]

        return output


class OpenDateInput:
    desc = "Выберите дату начало пириода "
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session["params"]["inputs"]["0"]["periodOpenDate"])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({"id": left, "name": left[0:10]})

        return output


class PeriodOpenDateInput:
    name = "Магазин"
    desc = "Выберите период"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "day", "name": "День"},
            {"id": "week", "name": "Неделя"},
            {"id": "fortnight", "name": "Две недели"},
            {"id": "month", "name": "Месяц"},
            {"id": "two months", "name": "Два месяца"},
        ]

        return output


class CloseDateInput:
    desc = "Выберите дату окончание пириода "
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = session["params"]["inputs"]["0"]["openDate"]
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)

        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({"id": left, "name": left[0:10]})

        return output


def get_inputs(session: Session):
    period = ["day", "week", "fortnight", "month"]
    if session.params["inputs"]["0"]:
        if "period" in session.params["inputs"]["0"]:
            if session.params["inputs"]["0"]["period"] == "day":
                return {}
            if session.params["inputs"]["0"]["period"] not in period:
                return {"openDate": OpenDatePastInput}
            else:
                return {
                    # 'cash_income1': CachIncome1Input,
                    "openDate": OpenDatePastInput,
                    "closeDate": CloseDatePastInput,
                }
    else:
        return {
            "period": PeriodDateInput,
        }


def generate(session: Session):
    params = session.params["inputs"]["0"]

    period = get_period(session)
    since = period["since"]
    until = period["until"]

    shops = [
        "20220501-DDCF-409A-8022-486441F27458",
        # '20200630-3E0D-4061-80C1-F7897E112F00',
        "20220501-9ADF-402C-8012-FB88547F6222",
        "20220501-3254-40E5-809E-AC6BB204D373",
        "20230214-33E5-4085-80A3-28C177E34112",
        "20220501-4D25-40AD-80DA-77FAE02A007E",
        "20220601-4E97-40A5-801B-1A29127AFA8B",
        "20220430-A472-40B8-8077-2EE96318B7E7",
    ]

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
    x_type = ["SELL", "PAYBACK"]

    sales_data = {}

    for k, v in shops_id_2.items():
        sum_sales = 0
        shop = Shop.objects(uuid=v).only("name").first()
        documents_sales = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": v,
                "x_type": {"$in": x_type},
                # 'transactions.commodityUuid': {'$in': products_uuid}
            }
        )
        # pprint(documents)

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
    pprint(report_data)
    # Отображаем график
    fig.show()
    return [report_data], image_buffer
