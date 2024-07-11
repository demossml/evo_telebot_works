from arrow import utcnow, get
from bd.model import Shop, AfsRequest, Employees, GetTime, Status, TimeSync

from pprint import pprint
from reports.util import (
    get_plan,
    analyze_sales_parallel,
)
import plotly.express as px
from io import BytesIO
import time
import logging
import sys

logger = logging.getLogger(__name__)


def status_shop(shop_id: str) -> bool:
    # Получаем объект статуса из базы данных для указанного магазина со статусом "deleted"
    doc_status = Status.objects(shop=shop_id, status="deleted").first()
    # Возвращаем True, если объект не найден или его статус "restore", иначе возвращаем False
    return not (doc_status and doc_status.status != "restore")


# # Функция для отправки сообщений по расписанию
def send_scheduled_message():
    since = utcnow().replace(hour=2).isoformat()

    result = {}
    for shop in Shop.objects():
        if status_shop(shop["uuid"]):
            documents = GetTime.objects(
                __raw__={"openingData": {"$gte": since}, "shopUuid": shop["uuid"]}
            )

            result[shop["name"]] = "ЕЩЕ НЕ ОТКРЫТА!!!"

            for doc in documents:
                user_id = str(doc.user_id)
                employees = [
                    element["name"]
                    for element in Employees.objects(lastName=user_id).only("name")
                ]
                if doc["openingData"]:
                    result[shop["name"]] = "{} {}".format(
                        employees[0], doc["openingData"][11:16]
                    )
    return [result]


def format_message_list4(obj):
    text = ""  # Создаем пустую строку для хранения текста сообщений.
    messages = []  # Создаем пустой список для хранения отформатированных сообщений.

    if len(obj) > 0:  # Проверяем, есть ли объекты в списке.
        for i in obj:  # Проходим по каждому объекту в списке.
            for k, v in i.items():  # Проходим по каждой паре ключ-значение в объекте.
                key = str(k)  # Преобразуем ключ в строку.
                val = str(v)  # Преобразуем значение в строку.
                total_len = len(key) + len(
                    val
                )  # Вычисляем общую длину ключа и значения.
                pad = (
                    30 - total_len % 30
                )  # Вычисляем количество пробелов, чтобы выровнять текст.

                text += key  # Добавляем ключ к тексту.

                if pad > 0:  # Если нужно добавить пробелы для выравнивания,
                    text += " " * pad  # добавляем их.

                if total_len > 30:  # Если общая длина превышает 30 символов,
                    text += " " * 2  # добавляем 2 дополнительных пробела.

                text += str(v)  # Добавляем значение к тексту.
                text += "\n"  # Добавляем перевод строки между ключами и значениями.
            text += "\n"  # Добавляем пустую строку после каждого объекта.
            text += "******************************"  # Добавляем разделительную строку.
            text += "\n"

        text += ""  # Пустая строка (это выглядит как ошибка, потому что она ничего не делает).
        index = 0  # Начальный индекс для разделения текста на части.
        size = 4000  # Максимальная длина каждой части сообщения.
        while len(text) > 0:  # Пока есть текст для обработки:
            part = text[
                index : index + size
            ]  # Выбираем часть текста длиной не более 4000 символов.
            index = part.rfind(
                "\n"
            )  # Находим последний символ перевода строки в части.
            if index == -1:  # Если символ перевода строки не найден,
                index = len(text)  # используем всю часть текста.
            part = text[
                0:index
            ]  # Выбираем часть текста до найденного символа перевода строки.
            messages.append(
                "```\n" + part + "\n```"
            )  # Добавляем часть текста в список сообщений,
            text = text[index:].strip()  # и удаляем ее из исходного текста.

        return messages  # Возвращаем список отформатированных сообщений.


def get_electro_sales_plan() -> list[dict]:
    start_time = time.time()

    data_resul = {}
    data_sale = analyze_sales_parallel()

    sales_data = {}

    for k, v in data_sale.items():
        doc_status = Status.objects(shop=k, status="deleted").first()
        if not doc_status:
            plan = get_plan(k)
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
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"Время выполнения функции sync_evo: {execution_time:.2f} секунд")

    return [data_resul], image_buffer
