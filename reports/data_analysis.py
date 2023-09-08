from bd.model import Shop, Products, Documents, Session, Employees
from .util import get_intervals, get_period, get_shops_user_id, get_shops
from pprint import pprint
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from io import BytesIO


from .inputs import (
    ReportDataAnalysisInput,
    ShopAllInput,
    GroupInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
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
                return {"openDate": OpenDatePastInput, "closeDate": CloseDatePastInput}
        if session.params["inputs"]["0"]["report"] == "analysis_sales_shops":
            return {
                "period": PeriodDateInput,
            }
        if session.params["inputs"]["0"]["report"] == "analysis_outcome_shops":
            return {
                "period": PeriodDateInput,
            }
    else:
        return {"report": ReportDataAnalysisInput}


def generate(session: Session):
    # Получение параметров из сессии
    params = session.params["inputs"]["0"]

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
                ).first()
                # Если есть информация о закрытии дня
                if documents_close_session:
                    sum_sales += float(documents_close_session.closeResultSum)

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
                sales_data.update({shop.name: sum_sales})

        report_data = {
            "Начало периода:": since[0:10],
            "Окончание периода:": until[0:10],
        }
        for k, v in sales_data.items():
            report_data.update({k: f"{v}₽"})

        # sales_list = []
        # for k, v in sales_data.items():
        #     sales_list.append(f"{k} {v}₽")
        # Извлекаем названия магазина и суммы продаж
        shop_names = list(sales_data.keys())
        sum_sales_ = list(sales_data.values())

        # Создаем круговую диаграмму
        plt.figure(figsize=(10, 10))
        # Устанавливаем размер шрифта для процентных значений на диаграмме
        plt.rcParams["font.size"] = 14  # Здесь задайте желаемый размер шрифта
        plt.pie(
            sum_sales_,
            labels=shop_names,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontweight": "bold"},
        )
        plt.axis("equal")  # Задаем равное соотношение сторон для круга

        # Рассчитываем сумму всех продаж
        total_sales = sum(sum_sales_)

        report_data.update({"Итого выручка:": f"{total_sales}₽"})

        # Добавляем названия магазинов поочередно в новые строки и выравниваем их по первому символу в верхний правый угол
        # for i, shop_name in enumerate(sales_list):
        #     plt.text(
        #         0.8,
        #         1.0 - i * 0.04,
        #         shop_name,
        #         transform=plt.gca().transAxes,
        #         fontsize=12,
        #         va="center",
        #     )

        # Создаем объект BytesIO для сохранения изображения в память
        image_buffer = BytesIO()

        # Сохраняем диаграмму в объект BytesIO
        plt.savefig(image_buffer, format="png")

        # Очищаем буфер изображения и перемещаем указатель в начало
        image_buffer.seek(0)

        # Закрываем текущий график, чтобы он не отображался
        plt.close()
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
                documents_close_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": new_shop_id,
                        "x_type": "CLOSE_SESSION",
                    }
                ).first()
                # Если есть информация о закрытии дня
                if documents_close_session:
                    sum_sales += float(documents_close_session.closeResultSum)

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
                sales_data.update({shop.name: sum_sales})

        report_data = {
            "Начало периода:": since[0:10],
            "Окончание периода:": until[0:10],
        }
        for k, v in sales_data.items():
            report_data.update({k: f"{v}₽"})

        # sales_list = []
        # for k, v in sales_data.items():
        #     sales_list.append(f"{k} {v}₽")
        # Извлекаем названия магазина и суммы продаж
        shop_names = list(sales_data.keys())
        sum_sales_ = list(sales_data.values())

        # Создаем круговую диаграмму
        plt.figure(figsize=(10, 10))
        # Устанавливаем размер шрифта для процентных значений на диаграмме
        plt.rcParams["font.size"] = 14  # Здесь задайте желаемый размер шрифта
        plt.pie(
            sum_sales_,
            labels=shop_names,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontweight": "bold"},
        )
        plt.axis("equal")  # Задаем равное соотношение сторон для круга

        # Рассчитываем сумму всех продаж
        total_sales = sum(sum_sales_)

        report_data.update({"Итого выручка:": f"{total_sales}₽"})

        # Добавляем названия магазинов поочередно в новые строки и выравниваем их по первому символу в верхний правый угол
        # for i, shop_name in enumerate(sales_list):
        #     plt.text(
        #         0.8,
        #         1.0 - i * 0.04,
        #         shop_name,
        #         transform=plt.gca().transAxes,
        #         fontsize=12,
        #         va="center",
        #     )

        # Создаем объект BytesIO для сохранения изображения в память
        image_buffer = BytesIO()

        # Сохраняем диаграмму в объект BytesIO
        plt.savefig(image_buffer, format="png")

        # Очищаем буфер изображения и перемещаем указатель в начало
        image_buffer.seek(0)

        # Закрываем текущий график, чтобы он не отображался
        plt.close()
        return [report_data], image_buffer
