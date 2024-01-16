from arrow import utcnow, get
from bd.model import Session, CashRegister
from pprint import pprint
from .util import period_to_date, get_intervals

name = "🔛💲 Движение д/с ➡️".upper()
desc = "Собирает данные о движение денежных средст за пириод"
mime = "text"


class ReportsInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "get_sales_by_shops", "name": "В ₽ ПО ВСЕМ ТТ"},
            {
                "id": "get_sales_by_shop_product_group_unit",
                "name": "В шт по группе товаров по всем ТТ",
            },
            {
                "id": "get_sales_by_shop_product_group_rub",
                "name": "В ₽ по группе товаров ",
            },
            {
                "id": "get_sales_product_group_unit_by_shop",
                "name": "В шт по группе товаров по всем ТТ",
            },
            {
                "id": "get_sales_product_product_unit_by_shop",
                "name": "В шт по товару по всем ТТ",
            },
            {
                "id": "get_sales_product_group_unit_by_shop",
                "name": "В шт по группе товаров по всем ТТ",
            },
        )

        return output


class X_typeInput:
    name = "Магазин"
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "CASH_INCOME", "name": "Внесение".upper()},
            {"id": "CASH_OUTCOME", "name": "Выплаты ".upper()},
            {"id": "CASH_OUTCOME", "name": "Выплаты ".upper()},
        )
        return output


class PeriodOpenDateInput:
    name = "Магазин"
    desc = "Выберите период 🗓".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "day", "name": "День ➡️".upper()},
            {"id": "week", "name": "Неделя ➡️".upper()},
            {"id": "fortnight", "name": "Две недели ➡️".upper()},
            {"id": "month", "name": "Месяц ➡️".upper()},
            {"id": "two months", "name": "Два месяца ➡️".upper()},
            {"id": "three months", "name": "Три месяца ➡️".upper()},
            {"id": "four months", "name": "Четыре месяца ➡️".upper()},
            {"id": "five months", "name": "Пять месяца ➡️".upper()},
            {"id": "six months", "name": "Шесть месяца ➡️".upper()},
            {"id": "seven months", "name": "Четыре месяца ➡️".upper()},
        )

        return output


class baseInput:
    name = "Магазин"
    desc = "Выберите основание"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "All", "name": "Всё ➡️".upper()},
            {"id": "Аренда1", "name": "Аренда1 ➡️".upper()},
            {"id": "ЗП", "name": "ЗП ➡️".upper()},
            {"id": "ЗП Д", "name": "ЗП Д ➡️".upper()},
            {"id": "Аренда", "name": "Аренда ➡️".upper()},
            {"id": "ГСМ", "name": "ГСМ ➡️".upper()},
            {"id": "Мороженое", "name": "Мороженое ➡️".upper()},
            {"id": "Закупка Товара", "name": "Закупка Товара ➡️".upper()},
            {"id": "Прочие", "name": "Прочие ➡️".upper()},
        )
        return output


class OpenDateInput:
    desc = "Выберите дату начало пириода 📅".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session["params"]["inputs"]["periodOpenDate"])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({"id": left, "name": "{} ➡️".format(left[0:10])})

        return output


class PeriodCloseDateInput:
    name = "Магазин"
    desc = "Выберите период"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "day", "name": "День"},
            {"id": "week", "name": "Неделя"},
            {"id": "fortnight", "name": "Две недели"},
            {"id": "month", "name": "Месяц"},
        )

        return output


class CloseDateInput:
    desc = "Выберите дату окончание пириода "
    type = "SELECT"

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = session["params"]["inputs"]["openDate"]
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)

        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({"id": left, "name": "{} ➡️".format(left[0:10])})

        return output


class baseInput:
    desc = "Основание:"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "Аренда1", "name": "Аренда1 ➡️".upper()},
            {"id": "ЗП", "name": "ЗП ➡️".upper()},
            {"id": "ЗП Д", "name": "ЗП Д ➡️".upper()},
            {"id": "Аренда", "name": "Аренда ➡️".upper()},
            {"id": "ГСМ", "name": "ГСМ ➡️".upper()},
            {"id": "Закупка Товара", "name": "Закупка Товара ➡️".upper()},
            {"id": "Прочие", "name": "Прочие ➡️".upper()},
        )

        return output


def get_inputs(session: Session):
    return {
        "x_type": X_typeInput,
        "periodOpenDate": PeriodOpenDateInput,
        # 'base': baseInput,
        "openDate": OpenDateInput,
        "closeDate": CloseDateInput,
    }


def generate(session: Session):
    params = session.params["inputs"]["0"]

    since = get(params["openDate"]).replace(hour=3, minute=00).isoformat()

    until = get(params["closeDate"]).replace(hour=23, minute=00).isoformat()
    pprint(until)
    pprint(since)
    x_type = params["x_type"]
    if x_type == "CASH_INCOME":
        who = "От кого"
        identifier = "Внесение"
    else:
        who = "Кому"
        identifier = "Выплаты"
    document = CashRegister.objects(
        __raw__={
            "closeDate": {"$gte": since, "$lt": until},
            "payment": "cash",
            "x_type": x_type,
            # 'base': params['base']
        }
    )
    result = []
    for doc in document:
        result.append(
            {
                who: doc["who"],
                "Дата:": doc["closeDate"][0:19],
                "Основание:": doc["base"],
                "Комментарий:": doc["comment"],
                "Сумма:": "{}₽".format(doc["cash"]),
                "№:": doc["number"],
                "": identifier,
            }
        )
    return result
