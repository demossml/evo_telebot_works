from bd.model import (
    Shop,
    Products,
    Documents,
    Employees,
    Session,
    Plan,
    GroupUuidAks,
    CashRegister,
)
from arrow import utcnow, get
from typing import List, Tuple
from pprint import pprint
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from io import BytesIO


# Принимает словарь с данными о продукте


def format_sell_groups(_dict: dict, since: str, until: str) -> list[dict]:
    """
    :param _dict: словарь с данными о продукте

    :return: [
    {
        '1 Наименование:': str,
        '2 Остаток:': str,
        '3 Цена поставки:': str,
        '4 Цена продажи:': str,
        '5 Сумма(цена поставки):': str
    }

    ]
    """
    result = []
    cost_price = 0
    for k, v in _dict.items():
        prod = Products.objects(uuid=k, group__exact=False).first()
        result.append(
            {
                "1 Наименование:": prod.name,
                "2 Остаток:": "{} {}.".format(v["col"], prod.measureName),
                "3 Цена поставки: ": "{} ₱".format(prod.costPrice),
                "4 Цена продажи:": "{} ₱".format(prod.price),
                "5 Сумма(цена поставки):": "{} ₱".format(v["sum"]),
            }
        )
        cost_price += prod.costPrice
    result.append(
        {
            "⬇️⬇️⬇️⬇️Итого⬇️⬇️⬇️⬇️".upper(): " ",
            "Цена продажи:".upper(): f"{cost_price} ₱",
            "Начало периода:".upper(): since[0:10],
            "Окончание периода:".upper(): until[0:10],
        }
    )

    return result


def get_products(session: Session, shop_id: str) -> object:
    """
    :param session: Объект сессии пользователя
    :param shop_id: Список идентификаторов магазинов (UUID)
    :return: Объект с данными по продуктам магазина
    """
    # Определить роль сотрудника в сессии
    if session.employee.role == "CASHIER":
        # Если роль сотрудника - кассир, вернуть продукты с фильтрами
        # для кассиров, исключая продукты с указанным UUID
        return Products.objects(shop_id__in=shop_id, group__exact=True, uuid__in=None)
    elif session.employee.role == "ADMIN":
        # Если роль сотрудника - администратор, вернуть продукты с фильтрами
        # для администраторов магазина
        return Products.objects(shop_id__in=shop_id, group__exact=True)
    else:
        # Если роль сотрудника не определена или не соответствует "CASHIER" или "ADMIN",
        # можно добавить обработку других ролей или выбросить исключение
        raise ValueError("Недопустимая роль сотрудника в сессии")


def get_products_shops(session: Session, shop_id: list) -> object:
    """
    :param session:
    :param shop_id: uuid: str магазина
    :return: Данные по продуктам магазина
    """
    if session.employee.role == "CASHIER":
        return Products.objects(shop_id__in=shop_id, group__exact=True, uuid__in=None)
    if session.employee.role == "ADMIN":
        return Products.objects(shop_id__in=shop_id, group__exact=True)


def get_group(session: Session) -> dict[str:str]:
    """
    :param session:
    :return: {uuid: name} группы
    """
    uuid = []
    for item in Employees.objects(lastName=str(session.user_id)):
        for store in item.stores:
            if store not in uuid:
                uuid.append(store)

    group = {}
    for element in uuid:
        for item in Products.objects(shop_id__exact=element, group__exact=True):
            if item["uuid"] not in group:
                group.update({item["uuid"]: item["name"]})
    return group


def get_shops(session: Session) -> dict[str : list | str]:
    """
    :param session:
    :return: {
                'shop_id': ['shop_id', ...],
                'shop_name': 'name'
            }
    """
    # Получение параметров из сессии
    params = session.params["inputs"]["0"]

    # Создание списка для хранения уникальных идентификаторов магазинов (uuid)
    uuid = []
    # Поиск сотрудников с заданной фамилией (session.user_id) и итерация по их магазинам
    for item in Employees.objects(lastName=str(session.user_id)):
        for store in item.stores:
            if store not in uuid:
                uuid.append(store)
    # Проверка наличия параметра "shop" в запросе
    if "shop" in params:
        if params["shop"] == "all":
            # Возвращаем информацию о всех магазинах
            return {
                "shop_id": [item["uuid"] for item in Shop.objects(uuid__in=uuid)],
                "shop_name": "Все".upper(),
            }
        else:
            # Возвращаем информацию о конкретном магазине, указанном в параметре "shop"
            shop = Shop.objects(uuid__exact=params["shop"]).only("name").first()
            return {"shop_id": [params["shop"]], "shop_name": shop.name}

    else:
        # Если параметр "shop" отсутствует, возвращаем информацию о всех магазинах
        return {
            "shop_id": [item["uuid"] for item in Shop.objects(uuid__in=uuid)],
            "shop_name": "Все".upper(),
        }


def get_shops_last_room(session: Session) -> dict[str : list | str]:
    """
    :param session:
    :return: {
                'shop_id': ['shop_id', ...],
                'shop_name': 'name'
            }
    """
    # Получение параметров из сессии

    room = session["room"]
    params = session.params["inputs"][room]

    # Создание списка для хранения уникальных идентификаторов магазинов (uuid)
    uuid = []
    # Поиск сотрудников с заданной фамилией (session.user_id) и итерация по их магазинам
    for item in Employees.objects(lastName=str(session.user_id)):
        for store in item.stores:
            if store not in uuid:
                uuid.append(store)
    # Проверка наличия параметра "shop" в запросе
    if "shop" in params:
        if params["shop"] == "all":
            # Возвращаем информацию о всех магазинах
            return {
                "shop_id": [item["uuid"] for item in Shop.objects(uuid__in=uuid)],
                "shop_name": "Все".upper(),
            }
        else:
            # Возвращаем информацию о конкретном магазине, указанном в параметре "shop"
            shop = Shop.objects(uuid__exact=params["shop"]).only("name").first()
            return {"shop_id": [params["shop"]], "shop_name": shop.name}

    else:
        # Если параметр "shop" отсутствует, возвращаем информацию о всех магазинах
        return {
            "shop_id": [item["uuid"] for item in Shop.objects(uuid__in=uuid)],
            "shop_name": "Все".upper(),
        }


def get_shops_user_id(session: Session) -> object:
    """
    Получить магазины, связанные с пользователем Telegram бота.

    :param session: Объект сессии пользователя.
    :return: Магазины, связанные с пользователем.
    """
    # Создаем пустой список для хранения уникальных идентификаторов магазинов (uuid).
    uuid = []
    # Итерируемся по сотрудникам с фамилией, равной user_id из сессии
    for item in Employees.objects(lastName=str(session.user_id)):
        # Для каждого найденного сотрудника итерируемся по его магазинам.
        for store in item.stores:
            # Проверяем, не находится ли магазин уже в списке UUID.
            if store not in uuid:
                # Добавляем магазина в список UUID, если его там нет.
                uuid.append(store)
    # Возвращаем объект Shop, в котором UUID магазина содержатся в списке UUID
    return Shop.objects(uuid__in=uuid)


def get_shops_uuid_user_id(session: Session) -> list:
    """
    :param session: Сессия пользователя
    :return: Список уникальных UUID магазинов, связанных с пользователем
    """
    # Создаем пустой список для хранения уникальных UUID магазинов
    uuid = []
    # Итерируемся по всем сотрудникам с фамилией, совпадающей с идентификатором пользователя
    for item in Employees.objects(lastName=str(session.user_id)):
        # Для каждого сотрудника итерируемся по списку магазинов, к которым он привязан
        for store in item.stores:
            # Проверяем, не был ли магазин уже добавлен в список UUID
            if store not in uuid:
                # Если магазина еще нет в списке, добавляем его
                uuid.append(store)
    # Возвращаем список уникальных UUID магазинов
    return uuid


# Определение состояния сеанса:
# 1. Проверка наличия элементов в списке id_
# 2. Получение списка магазинов в зависимости от состояния сеанса и параметров
# 3. Формирование и возврат списка магазинов
def get_shops_in(session: Session, _in=[], id_=[]) -> object:
    uuid = []
    uuid_id = (
        "20220501-11CA-40E0-8031-49EADC90D1C4",
        "20220501-DDCF-409A-8022-486441F27458",
        "20220501-9ADF-402C-8012-FB88547F6222",
        "20220501-3254-40E5-809E-AC6BB204D373",
        "20220501-CB2E-4020-808C-E3FD3CB1A1D4",
        "20220501-4D25-40AD-80DA-77FAE02A007E",
        "20220430-A472-40B8-8077-2EE96318B7E7",
        "20220506-AE5B-40BA-805B-D8DDBD408F24",
    )

    if len(id_) > 0:
        # pprint(1)
        users = [uuid_id]
    else:
        # pprint(2)
        users = [
            element.stores
            for element in Employees.objects(lastName=str(session.user_id))
        ]

    # pprint(users)
    for i in users:
        for e in i:
            if e in _in:
                if e not in uuid:
                    # pprint(e)
                    uuid.append(e)
            if session.user_id == 490899906:
                for el in _in:
                    if el not in uuid:
                        uuid.append(el)
    # pprint(uuid)
    return Shop.objects(uuid__in=uuid)


def period_to_date(period: str) -> utcnow:
    """
    :param period: строка, представляющая период времени ("day", "week", "fortnight", "month", "two months", "6 months", "12 months", "24 months", "48 months")
    :return: строка с датой и временем в ISO формате, отстоящая на указанный период времени назад от текущего времени в UTC с временем 03:00.
    """
    # Проверяем значение параметра "period" и выполняем соответствующее смещение времени
    if period == "day":
        return utcnow().to("local").replace(hour=3, minute=00).isoformat()
    if period == "week":
        return (
            utcnow().to("local").shift(days=-7).replace(hour=3, minute=00).isoformat()
        )
    if period == "fortnight":
        return (
            utcnow().to("local").shift(days=-14).replace(hour=3, minute=00).isoformat()
        )
    if period == "month":
        return (
            utcnow().to("local").shift(months=-1).replace(hour=3, minute=00).isoformat()
        )
    if period == "two months":
        return (
            utcnow().to("local").shift(months=-2).replace(hour=3, minute=00).isoformat()
        )
    if period == "6 months":
        return (
            utcnow().to("local").shift(months=-6).replace(hour=3, minute=00).isoformat()
        )
    if period == "12 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-12)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    if period == "24 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-24)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    if period == "48 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-48)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    raise Exception("Period is not supported")


def period_first_day_of_the_month(period: str) -> utcnow:
    """
    :param period: строка, представляющая период времени ("day", "week", "fortnight", "month", "two months", "6 months", "12 months", "24 months", "48 months")
    :return: строка с датой и временем в ISO формате, отстоящая на указанный период времени назад от текущего времени в UTC с временем 03:00.
    """
    # Проверяем значение параметра "period" и выполняем соответствующее смещение времени
    if period == "day":
        return utcnow().to("local").replace(hour=3, minute=00).isoformat()
    if period == "week":
        return (
            utcnow().to("local").shift(days=-7).replace(hour=3, minute=00).isoformat()
        )
    if period == "fortnight":
        return (
            utcnow().to("local").shift(days=-14).replace(hour=3, minute=00).isoformat()
        )
    if period == "month":
        return (
            utcnow()
            .to("local")
            .shift(months=-1)
            .replace(day=1, hour=3, minute=00)
            .isoformat()
        )
    if period == "two months":
        return (
            utcnow()
            .to("local")
            .shift(months=-2)
            .replace(day=1, hour=3, minute=00)
            .isoformat()
        )
    if period == "6 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-6)
            .replace(day=1, hour=3, minute=00)
            .isoformat()
        )
    if period == "12 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-12)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    if period == "24 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-24)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    if period == "48 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-48)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    raise Exception("Period is not supported")


def period_to_date_2(period: str) -> utcnow:
    """
    :param period: day, week,  fortnight, month, two months,
    :return: utcnow + period
    """
    if period == "day":
        return utcnow().replace(hour=3, minute=00).isoformat()
    if period == "week":
        return utcnow().shift(days=7).replace(hour=3, minute=00).isoformat()
    if period == "fortnight":
        return utcnow().shift(days=14).replace(hour=3, minute=00).isoformat()
    if period == "month":
        return utcnow().shift(months=1).replace(hour=3, minute=00).isoformat()
    if period == "two months":
        return utcnow().shift(months=2).replace(hour=3, minute=00).isoformat()
    if period == "6 months":
        return utcnow().shift(months=6).replace(hour=3, minute=00).isoformat()
    if period == "12 months":
        return utcnow().shift(months=12).replace(hour=3, minute=00).isoformat()
    if period == "24 months":
        return utcnow().shift(months=24).replace(hour=3, minute=00).isoformat()
    if period == "48 months":
        return utcnow().shift(months=48).replace(hour=3, minute=00).isoformat()
    raise Exception("Period is not supported")


# Получить интервалы дат между минимальной и максимальной датами с определенным шагом в указанных единицах измерения (unit: days, weeks, fortnights, months).
# Возвращает список кортежей (минимальная дата, максимальная дата).
def get_intervals(
    min_date: str, max_date: str, unit: str, measure: float
) -> List[Tuple[str, str]]:
    """
    :param min_date: дата начала пириода
    :param max_date: дата окончания пириода
    :param unit: days, weeks,  fortnights, months
    :param measure: int шаг
    :return: List[Tuple[min_date, max_date]]
    """
    output = []
    while min_date < max_date:
        # Получить новую дату, добавив или вычтя указанное количество времени в указанных единицах измерения
        temp = get(min_date).shift(**{unit: measure}).isoformat()
        # Записать пару дат (min_date, min(temp, max_date)) в список выходных данных
        output.append((min_date, min(temp, max_date)))
        # Обновить min_date на новую дату temp
        min_date = temp
    return output


def get_employees(session: Session) -> object:
    """
    Получает список сотрудников пользователя Telegram бота на основе их session.user_id.

    :param session: Сеанс пользователя бота.
    :return: Объект (список или другая структура), содержащий информацию о сотрудниках.
    """
    # Инициализируем пустой список uuid для сохранения идентификаторов сотрудников
    uuid = []
    # Получаем список хранилищ (stores) сотрудников с фамилией, соответствующей session.user_id
    users = [
        element.stores for element in Employees.objects(lastName=str(session.user_id))
    ]
    # Итерируемся по списку хранилищ и добавляем их uuid в список uuid
    for i in users:
        for e in i:
            uuid.append(e)
    # Возвращаем  структуру, содержащую информацию о сотрудниках

    return Employees.objects(stores__in=uuid)


def get_employees(last_name: str) -> list:
    """
    Возвращает список UUID пользователей Telegram Bot, чья фамилия совпадает с заданной.

    :param last_name: Фамилия сотрудника для поиска.
    :return: Список UUID пользователей Telegram Bot.
    """
    # Используем список-выражение для получения UUID сотрудников, у которых фамилия совпадает с заданной.
    users = [element.uuid for element in Employees.objects(lastName=last_name)]

    # Возвращаем список UUID пользователей.
    return users


def get_products_all(session: Session, shop_id: list) -> dict[str:str]:
    """
    Получает список продуктов для указанных магазинов.

    :param shop_id: Список идентификаторов магазинов, для которых нужно получить продукты.
    :param session: Сессия (предположительно, объект сессии для взаимодействия с базой данных).
    :return: Словарь, содержащий информацию о продуктах в формате {'uuid': 'name'}.
    """
    # Создаем пустой словарь для хранения информации о продуктах
    result = {}
    for item in Products.objects(shop_id__in=shop_id, group__exact=True):
        # Если 'uuid' продукта еще не добавлен в результат, то добавляем его в словарь.
        if item["uuid"] not in result:
            # Добавляем информацию о продукте в словар
            result[item["uuid"]] = item["name"]
    # Возвращаем словарь с информацией о продуктах
    return result


def get_period(session: Session) -> dict[str:str]:
    """
    Функция get_period_day принимает объект сессии Session и возвращает словарь,
    содержащий информацию о временном периоде 'since' и 'until'.

    :param session:
    :return: {'since': str, 'until': str}
    """
    # Список возможных периодов
    period_in = ["day", "week", "fortnight", "month"]
    # Проверка, что указанный период находится в списке возможных периодов
    if session.params["inputs"]["0"]["period"] not in period_in:
        # Если период - "day", то 'since' устанавливаем в начало дня, а 'until' в конец дня
        return {
            "since": get(session.params["inputs"]["0"]["openDate"])
            .replace(day=1)
            .isoformat(),
            "until": get(session.params["inputs"]["0"]["openDate"])
            .ceil("month")
            .isoformat(),
        }
    # Если выбран период "day", возвращаем начальную дату как период "сегодня", а конечную - текущую дату и время
    if session.params["inputs"]["0"]["period"] == "day":
        return {
            "since": period_to_date(session.params["inputs"]["0"]["period"]),
            "until": utcnow().isoformat(),
        }
    # Если выбран другой период, возвращаем начальную и конечную дату с учетом указанных дат
    else:
        return {
            "since": get(session.params["inputs"]["0"]["openDate"])
            .replace(hour=3, minute=00)
            .isoformat(),
            "until": get(session.params["inputs"]["0"]["closeDate"])
            .replace(hour=23, minute=00)
            .isoformat(),
        }


def get_period_(session: Session) -> dict[str:str]:
    """
    Функция get_period_day принимает объект сессии Session и возвращает словарь,
    содержащий информацию о временном периоде 'since' и 'until'.

    :param session:
    :return: {'since': str, 'until': str}
    """
    room = session["room"]
    # pprint(room)
    # pprint(session.params["inputs"][room]["period"])
    # Список возможных периодов
    period_in = ("day", "week", "fortnight", "month")
    # Проверка, что указанный период находится в списке возможных периодов
    if session.params["inputs"][room]["period"] not in period_in:
        # Если период - "day", то 'since' устанавливаем в начало дня, а 'until' в конец дня
        return {
            "since": get(session.params["inputs"][room]["openDate"])
            .replace(day=1)
            .isoformat(),
            "until": get(session.params["inputs"][room]["openDate"])
            .ceil("month")
            .isoformat(),
        }
    # Если выбран период "day", возвращаем начальную дату как период "сегодня", а конечную - текущую дату и время
    if session.params["inputs"][room]["period"] == "day":
        return {
            "since": period_to_date(session.params["inputs"][room]["period"]),
            "until": utcnow().isoformat(),
        }
    # Если выбран другой период, возвращаем начальную и конечную дату с учетом указанных дат
    else:
        return {
            "since": get(session.params["inputs"][room]["openDate"])
            .replace(hour=3, minute=00)
            .isoformat(),
            "until": get(session.params["inputs"][room]["closeDate"])
            .replace(hour=23, minute=00)
            .isoformat(),
        }


def get_period_day(session: Session) -> dict[str:str]:
    """
    :param session:
    :return: {'since': str, 'until': str}
    """
    # Проверяем, является ли период "day"
    if session.params["inputs"]["0"]["period"] == "day":
        # Если период - "day", то возвращаем период с начала дня до конца дня
        return {
            "since": period_to_date(session.params["inputs"]["0"]["period"]),
            "until": get(period_to_date(session.params["inputs"]["0"]["period"]))
            .replace(hour=23, minute=59)
            .isoformat(),
        }

    else:
        # Если период не "day", то возвращаем весь день (от 00:01 до 23:59) указанной даты
        return {
            "since": get(session.params["inputs"]["0"]["openDate"])
            .replace(hour=0, minute=1)
            .isoformat(),
            "until": get(session.params["inputs"]["0"]["openDate"])
            .replace(hour=23, minute=59)
            .isoformat(),
        }


def get_period_order(session: Session) -> dict[str:str]:
    """
    :param session:
    :return: {'since': str, 'until': str}
    """
    # Получаем данные о периоде заказа
    data = get(period_to_date(session.params["inputs"]["0"]["period"]))
    pprint(data)
    if session.params["inputs"]["0"]["period"] == "day":
        # Строим диапазон "since" с началом дня и концом дня, сдвинутыми на 7 дней назад.
        return {
            "since": get(period_to_date(session.params["inputs"]["0"]["period"]))
            .shift(days=-7)
            .replace(hour=00, minute=1)
            .isoformat(),
            # Строим диапазон "since" с началом дня и концом дня, сдвинутыми на 7 дней назад.
            "until": utcnow().shift(days=-7).replace(hour=23, minute=59).isoformat(),
        }

    else:
        # В противном случае возвращаем период на основе даты открытия
        return {
            "since": get(session.params["inputs"]["0"]["openDate"])
            .shift(days=-7)
            .replace(hour=0, minute=1)
            .isoformat(),
            "until": get(session.params["inputs"]["0"]["openDate"])
            .shift(days=-7)
            .replace(hour=23, minute=59)
            .isoformat(),
        }


def get_commodity_balances(session: Session) -> dict[str:int]:
    """
    :param session:
    :return: {'uuid': str, 'quantity': init}
    """
    # Создаем пустой словарь для хранения балансов товаров
    commodity_balances = {}
    # Получаем параметры из сессии
    params = session.params["inputs"]["0"]
    # Список типов транзакций
    x_type = ("SELL", "PAYBACK", "ACCEPT")
    # Получаем список магазинов из функции get_shops
    shops = get_shops(session)
    shop_id = shops["shop_id"]
    # Итерируемся по идентификаторам магазинов
    for shop_uuid in shop_id:
        # Если параметр "group" равен "all", получаем все товары в магазине
        if params["group"] == "all":
            products = Products.objects(
                __raw__={
                    "shop_id": shop_uuid,
                }
            )
            # Устанавливаем название группы товаров как "Все"
            group_name = "Все"
        else:
            # Иначе получаем товары, принадлежащие определенной группе
            products = Products.objects(
                __raw__={"shop_id": shop_uuid, "parentUuid": params["group"]}
            )
            # Получаем информацию о группе товаров по ее идентификатору
            porod = Products.objects(uuid=params["group"], group__exact=True).first()
            # Устанавливаем название группы товаров
            group_name = porod.name
        # Получаем идентификаторы всех товаров в текущей группе
        products_uuid = [element.uuid for element in products]
        # Итерируемся по идентификаторам товаров
        for uuid in products_uuid:
            # Ищем документы, связанные с текущим товаром
            documents = (
                Documents.objects(
                    __raw__={
                        "shop_id": shop_uuid,
                        "x_type": {"$in": x_type},
                        "transactions.commodityUuid": uuid,
                    }
                )
                .order_by("-closeDate")
                .first()
            )

            if documents:
                for trans in documents["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        if trans["commodityUuid"] == uuid:
                            if documents.x_type == "SELL":
                                # Обновляем баланс товара при продаже
                                commodity_balances[trans["commodityUuid"]] = (
                                    trans["balanceQuantity"] - trans["quantity"]
                                )

                            if documents.x_type == "PAYBACK":
                                # Обновляем баланс товара при возврате
                                commodity_balances[trans["commodityUuid"]] = (
                                    trans["balanceQuantity"] + trans["quantity"]
                                )

                            if documents.x_type == "ACCEPT":
                                # Обновляем баланс товара при приемке
                                commodity_balances[trans["commodityUuid"]] = trans[
                                    "balanceQuantity"
                                ]
    # Возвращаем словарь с балансами товаров
    return commodity_balances


def get_commodity_balances_all(shop_id, products_uuid) -> dict[str:int]:
    """
    :param session:
    :return: {'uuid': str, 'quantity': init}
    """

    # Создаем пустой словарь для хранения балансов товаров
    x_type = ("SELL", "PAYBACK", "ACCEPT")

    quantity_data = {}

    for uuid in products_uuid:
        quantity = 0
        documents = (
            Documents.objects(
                __raw__={
                    "shop_id": shop_id,
                    "x_type": {"$in": x_type},
                    "transactions.commodityUuid": uuid,
                }
            )
            .order_by("-closeDate")
            .first()
        )
        if documents:
            for trans in documents["transactions"]:
                if trans["x_type"] == "REGISTER_POSITION":
                    if trans["commodityUuid"] == uuid:
                        if documents.x_type == "SELL":
                            # Обновляем баланс товара при продаже
                            quantity = trans["balanceQuantity"] - trans["quantity"]

                        if documents.x_type == "PAYBACK":
                            # Обновляем баланс товара при возврате
                            quantity = trans["balanceQuantity"] + trans["quantity"]

                        if documents.x_type == "ACCEPT":
                            # Обновляем баланс товара при приемке
                            quantity = trans["balanceQuantity"]
        # Возвращаем словарь с балансами товаров
        quantity_data.update({uuid: quantity})
    return quantity_data


def generate_plan():
    """
    Эта функция создает и возвращает планы для магазинов на основе определенных условий.
    """
    # Список идентификаторов групп
    group_id = (
        "78ddfd78-dc52-11e8-b970-ccb0da458b5a",
        "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
        "0627db0b-4e39-11ec-ab27-2cf05d04be1d",
        "2b8eb6b4-92ea-11ee-ab93-2cf05d04be1d",
        "8a8fcb5f-9582-11ee-ab93-2cf05d04be1d",
        "97d6fa81-84b1-11ea-b9bb-70c94e4ebe6a",
        "ad8afa41-737d-11ea-b9b9-70c94e4ebe6a",
        "568905bd-9460-11ee-9ef4-be8fe126e7b9",
        "568905be-9460-11ee-9ef4-be8fe126e7b9",
    )
    # Список идентификаторов для фильтрации магазинов
    _in = (
        "20190327-A48C-407F-801F-DA33CB4FBBE9",
        "20220202-B042-4021-803D-09E15DADE8A4",
        "20231001-6611-407F-8068-AC44283C9196",
        "20190411-5A3A-40AC-80B3-8B405633C8BA",
        "20220201-19C9-40B0-8082-DF8A9067705D",
        "20191117-BF71-40FE-8016-1E7E4A3A4780",
    )
    # Список идентификаторов магазинов на основе фильтрации
    uuid = (
        "20210712-1362-4012-8026-5A35685630B2",
        "20220222-6C28-4069-8006-082BE12BEB32",
        "20200630-3E0D-4061-80C1-F7897E112F00",
        "20210923-FB1F-4023-80F6-9ECB3F5A0FA8",
        "20220201-19C9-40B0-8082-DF8A9067705D",
        "20220201-8B00-40C2-8002-EF7E53ED1220",
        "20220201-A55A-40B8-8071-EC8733AFFA8E",
        "20220202-B042-4021-803D-09E15DADE8A4",
    )
    # Получение магазинов с использованием фильтрации
    shops = Shop.objects(__raw__={"uuid": {"$in": _in}})

    _dict = {}

    for shop in shops:
        if shop["uuid"] in uuid:
            period = [7, 14, 21, 28]
        else:
            period = [7, 14, 21, 28]
        for element in period:
            # Рассчитываем временные интервалы с использованием UTC времени
            since = utcnow().shift(days=-element).replace(hour=3, minute=00).isoformat()
            # pprint(since)
            until = (
                utcnow().shift(days=-element).replace(hour=21, minute=00).isoformat()
            )
            # Получаем продукты для магазина и группы товаров
            products = Products.objects(
                __raw__={"shop_id": shop["uuid"], "parentUuid": {"$in": group_id}}
            )

            products_uuid = [element.uuid for element in products]
            # pprint(products_uuid)
            # Определяем типы транзакций
            x_type = ("SELL", "PAYBACK")
            # Получаем документы из базы данных на основе фильтров
            documents = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop["uuid"],
                    "x_type": {"$in": x_type},
                    "transactions.commodityUuid": {"$in": products_uuid},
                }
            )

            sum_sell = 0
            # Вычисляем и добавляем результат в словарь
            if len(documents) > 0:
                sum_sell = 0
                for doc in documents:
                    for trans in doc["transactions"]:
                        if trans["x_type"] == "REGISTER_POSITION":
                            if trans["commodityUuid"] in products_uuid:
                                sum_sell += trans["sum"]
            else:
                sum_sell = 0
            pprint(sum_sell)
            # Устанавливаем значение _day
            if shop["uuid"] in uuid:
                _day = 4
            else:
                _day = 4
            # Обновляем словарь суммами продаж
            if shop["uuid"] in _dict:
                _dict[shop["uuid"]] += round(
                    (int(sum_sell) / _day + int(sum_sell) / 5 / 100 * 4)
                )
            else:
                _dict[shop["uuid"]] = round(
                    (int(sum_sell) / _day + int(sum_sell) / 5 / 100 * 4)
                )
    # Обновляем параметры плана в базе данных
    for k, v in _dict.items():
        params = {"closeDate": utcnow().isoformat(), "shop_id": k}

        if v < 3000:
            params["sum"] = int(3000)
        else:
            params["sum"] = v
        # print(params)
        Plan.objects(closeDate=utcnow().isoformat()).update(**params, upsert=True)
    # Возвращаем параметры плана
    return params


def remainder(shops_uuid: list) -> list[dict[str:str]]:
    x_type = ("SELL", "PAYBACK", "ACCEPT")

    result = {}
    for sh in shops_uuid:
        result[sh] = []
        shop = Shop.objects(uuid=sh).only("name").first()

        products = Products.objects(__raw__={"shop_id": sh, "group": False})
        # pprint(products)
        uuids = [i.uuid for i in products]
        # pprint(uuids)
        for uuid in uuids:
            product = Products.objects(uuid=uuid).first()
            # pprint(product)
            cost_price = product["costPrice"]
            # pprint(cost_price)
            documents = (
                Documents.objects(
                    __raw__={
                        "shop_id": sh,
                        "x_type": {"$in": x_type},
                        "transactions.commodityUuid": uuid,
                    }
                )
                .order_by("-closeDate")
                .first()
            )

            # pprint(documents)
            # pprint('e')
            if documents is not None:
                for trans in documents["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        if trans["commodityUuid"] == uuid:
                            if documents.x_type == "SELL":
                                if trans["balanceQuantity"] - trans["quantity"] > 0:
                                    result[sh].append(
                                        {
                                            trans["commodityUuid"]: trans[
                                                "balanceQuantity"
                                            ]
                                            - trans["quantity"]
                                        }
                                    )
                            if documents.x_type == "PAYBACK":
                                # pprint(trans)
                                if trans["balanceQuantity"] + trans["quantity"] > 0:
                                    result[sh].append(
                                        {
                                            trans["commodityUuid"]: trans[
                                                "balanceQuantity"
                                            ]
                                            + trans["quantity"]
                                        }
                                    )
                            if documents.x_type == "ACCEPT":
                                # pprint(documents.closeDate)
                                result[sh].append(
                                    {trans["commodityUuid"]: trans["quantity"]}
                                )
    return result


# Зп по назначенным группам аксессуаров
def get_aks_salary(shop_id: str, since_: str, until_: str) -> dict:
    """
    Возвращает информацию о зарплате сотрудников в отделе aks.

    Args:
        shop_id (str): Идентификатор магазина.
        since_ (str): Начальная дата для анализа продаж.
        until_ (str): Конечная дата для анализа продаж.

    Returns:
        dict: Словарь с информацией о продажах и бонусах сотрудников aks.
            - "accessory_sum_sell" (int): Сумма продаж аксессуаров.
            - "bonus_accessory" (int): Рассчитанный бонус сотрудникам за продажи аксессуаров.
    """
    # Получаем документы aks для указанного магазина и периода времени
    documents_aks = (
        GroupUuidAks.objects(
            __raw__={
                "closeDate": {"$lte": until_[:10]},
                "shop_id": shop_id,
                "x_type": "MOTIVATION_PARENT_UUID",
            }
        )
        .order_by("-closeDate")  # Сортировка по убыванию даты закрытия
        .first()
    )
    if documents_aks:
        # Получаем группу продуктов, связанных с документами aks
        group = Products.objects(
            __raw__={
                "shop_id": shop_id,
                "parentUuid": {"$in": documents_aks.parentUuids},
            }
        )
        # Получаем список UUID продуктов
        products_uuid = [i.uuid for i in group]
        # Получаем документы о продажах для указанного магазина, периода и продуктов aks
        documents_sale = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since_, "$lt": until_},
                "shop_id": shop_id,
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )
        # Вычисляем общую сумму продаж аксессуаров.
        sum_sales_aks = 0
        for doc in documents_sale:
            for trans in doc["transactions"]:
                if trans["x_type"] == "REGISTER_POSITION":
                    if trans["commodityUuid"] in products_uuid:
                        sum_sales_aks += trans["sum"]
        # Вычисляем бонус за продажу аксессуаров (5% от общей суммы продаж).
        return {
            "accessory_sum_sell": sum_sales_aks,
            "bonus_accessory": round(int(sum_sales_aks / 100 * 5) / 10) * 10,
        }
    else:
        # Если не найдено документов GroupUuidAks, возвращаем нули.
        return {
            "accessory_sum_sell": 0,
            "bonus_accessory": 0,
        }


# Зп по продаже мотивационого товара
def get_mot_salary(shop_id: str, since_: str, until_: str) -> dict:
    """
    Функция возвращает бонус мотивации для магазина на основе продаж и данных о мотивации.

    Args:
        shop_id (str): Идентификатор магазина.
        since_ (str): Начальная дата для анализа продаж (включительно).
        until_ (str): Конечная дата для анализа продаж (исключительно).

    Returns:
        dict: Словарь, содержащий бонус мотивации в виде "bonus_motivation".
    """

    # Запрашиваем данные о мотивации для магазина
    documents_mot = (
        GroupUuidAks.objects(
            __raw__={
                "closeDate": {"$lte": until_[:10]},
                "shop_id": shop_id,
                "x_type": "MOTIVATION_UUID",
            }
        )
        .order_by("-closeDate")
        .first()
    )
    if documents_mot:
        # Извлекаем идентификаторы продуктов из данных о мотивации
        products_uuid = [k for k, v in documents_mot.uuid.items()]
        # Запрашиваем данные о продажах продуктов в указанный период времени
        documents_sale = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since_, "$lt": until_},
                "shop_id": shop_id,
                "x_type": "SELL",
                "transactions.commodityUuid": {"$in": products_uuid},
            }
        )
        # Создаем словарь для хранения данных о зарплате
        dict_salary = {}

        for doc in documents_sale:
            for trans in doc["transactions"]:
                if trans["x_type"] == "REGISTER_POSITION":
                    if trans["commodityUuid"] in products_uuid:
                        # Если продукт уже присутствует в словаре, увеличиваем его количество
                        if trans["commodityUuid"] in dict_salary:
                            dict_salary[trans["commodityUuid"]] += trans["quantity"]
                        # Если продукта нет в словаре, добавляем его с количеством из текущей транзакции
                        else:
                            dict_salary[trans["commodityUuid"]] = trans["quantity"]
        # Инициализируем сумму мотивации
        sum_mot = 0
        # Вычисляем сумму мотивации на основе данных о продажах и мотивации
        for k, v in dict_salary.items():
            sum_mot += v * documents_mot.uuid[k]
        # Возвращаем бонус мотивации в виде словаря
        return {"bonus_motivation": int(sum_mot)}

    else:
        # Если данных о мотивации нет, возвращаем нулевой бонус мотивации
        return {"bonus_motivation": 0}


# План по группе, продажи, бонус за выполнение плана
def get_plan_bonus(shop_id: str, since_: str, until_: str) -> dict:
    """
    Функция возвращает информацию о бонусах за выполнение плана для магазина на основе данных о планах и продажах.

    Args:
        shop_id (str): Идентификатор магазина.
        since_ (str): Начальная дата периода.
        until_ (str): Конечная дата периода.

    Returns:
        dict: Словарь с информацией о бонусе:
            - "plan_motivation_prod": Заданный план продаж.
            - "sales_motivation_prod": Фактические продажи в периоде.
            - "bonus_motivation_prod": Рассчитанный бонус за выполнение плана.
    """

    # Поиск планов для магазина и периода
    plan_ = Plan.objects(
        __raw__={
            "closeDate": {"$gte": since_, "$lt": until_},
            "shop_id": shop_id,
        }
    )
    # Если нет найденных планов, генерируем новый
    if len(plan_) > 0:
        plan = Plan.objects(
            __raw__={
                "closeDate": {"$gte": since_, "$lt": until_},
                "shop_id": shop_id,
            }
        ).first()
    else:
        generate_plan()
        plan = Plan.objects(
            __raw__={
                "closeDate": {"$gte": since_, "$lt": until_},
                "shop_id": shop_id,
            }
        ).first()
    # Группы товаров для анализа
    group_id = (
        "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
        "568905bd-9460-11ee-9ef4-be8fe126e7b9",
        "2b8eb6b4-92ea-11ee-ab93-2cf05d04be1d",
        "568905be-9460-11ee-9ef4-be8fe126e7b9",
        "ad8afa41-737d-11ea-b9b9-70c94e4ebe6a",
        "8a8fcb5f-9582-11ee-ab93-2cf05d04be1d",
        "78ddfd78-dc52-11e8-b970-ccb0da458b5a",
    )
    # Поиск товаров в указанных группах
    products = Products.objects(
        __raw__={"shop_id": shop_id, "parentUuid": {"$in": group_id}}
    )
    # Список UUID товаров
    products_uuid = [element.uuid for element in products]
    # Типы транзакций, которые учитываем (продажи и возвраты)
    x_type = ("SELL", "PAYBACK")
    # Получаем документы с продажами и возвратами товаров из списка products_uuid
    documents_2 = Documents.objects(
        __raw__={
            "closeDate": {"$gte": since_, "$lt": until_},
            "shop_id": shop_id,
            "x_type": {"$in": x_type},
            "transactions.commodityUuid": {"$in": products_uuid},
        }
    )

    sum_sell_today = 0
    for doc_2 in documents_2:
        for trans_2 in doc_2["transactions"]:
            if trans_2["x_type"] == "REGISTER_POSITION":
                if trans_2["commodityUuid"] in products_uuid:
                    sum_sell_today += trans_2["sum"]
    # Получаем информацию о мотивации из последнего документа
    documents_motiv = (
        GroupUuidAks.objects(
            __raw__={
                "closeDate": {"$lte": until_[:10]},
                "shop_id": shop_id,
                "x_type": "MOTIVATION",
            }
        )
        .order_by("-closeDate")
        .first()
    )
    # Функция для расчета бонуса по выполнению плана
    if documents_motiv:
        if sum_sell_today >= plan.sum:
            return {
                "plan_motivation_prod": plan.sum,
                "sales_motivation_prod": sum_sell_today,
                "bonus_motivation_prod": documents_motiv.motivation,
            }
        else:
            return {
                "plan_motivation_prod": plan.sum,
                "sales_motivation_prod": sum_sell_today,
                "bonus_motivation_prod": 0,
            }

    else:
        return {
            "plan_motivation_prod": plan.sum,
            "sales_motivation_prod": sum_sell_today,
            "bonus_motivation_prod": 0,
        }


# Функция для получения оклада продавцов в магазине
def get_salary(shop_id: str, until_: str) -> dict:
    """
    Возвращает оклад продавцов в магазине до указанной даты.

    Args:
        shop_id (str): Идентификатор магазина.
        until_ (str): Дата, до которой нужно получить оклад (включительно).

    Returns:
        dict: Словарь с информацией о окладе. Если информация найдена, то содержит "salary",
              иначе "salary" равно 0.
    """

    # Ищем документы о зарплате продавцов в указанном магазине до указанной даты
    documents_salary = GroupUuidAks.objects(
        __raw__={
            "closeDate": {"$lte": until_[:10]},
            "shop_id": shop_id,
            "x_type": "SALARY",
        }
    ).first()
    # Если найдена информация о зарплате, возвращаем ее
    if documents_salary:
        return {
            "salary": documents_salary.salary,
        }
    else:
        # Если документ не найден, возвращаем нулевую зарплату (0)
        return {
            "salary": 0,
        }


# Функция для получения доплаты к окладу продавцов на основе их идентификатора и даты окончания
def get_surcharge(employee_uuid: str, until_: str) -> dict:
    """
    Функция для получения доплаты к окладу продавцов.

    Args:
        employee_uuid (str): Уникальный идентификатор сотрудника.
        until_ (str): Дата (включительно), до которой нужно получить доплату.

    Returns:
        dict: Словарь, содержащий информацию о доплате к окладу:
            - "surcharge" (int): Размер доплаты, если есть, или 0, если доплаты нет.
    """
    # pprint(employee_uuid)
    # Ищем документы о доплатах к окладу для указанного сотрудника и даты окончания
    documents_surcharge = (
        GroupUuidAks.objects(
            __raw__={
                "closeDate": {"$lte": until_[:10]},
                "employee_uuid": employee_uuid,
                "x_type": "ASSING_A_SURCHARGE",
            }
        )
        .order_by("-closeDate")
        .first()
    )
    # pprint(documents_surcharge)
    # Если есть информация о доплате, возвращаем её
    if documents_surcharge:
        return {
            "surcharge": documents_surcharge.surcharge,
        }
    else:
        # Если информации нет, возвращаем 0
        return {
            "surcharge": 0,
        }


def get_total_salary(
    employee_uuid: str, shop_id: str, since_: str, until_: str
) -> dict:
    """
    Возвращает структуру, содержащую информацию о заработной плате сотрудника.

    Args:
        employee_uuid (str): Уникальный идентификатор сотрудника.
        shop_id (str): Идентификатор магазина.
        since_ (str): Дата начала периода.
        until_ (str): Дата окончания периода.

    Returns:
        dict: Словарь с информацией о заработной плате сотрудника.

    Структура словаря:
    {
        "accessory_sum_sell": int,         # Сумма продаж аксессуаров
        "bonus_accessory": int,           # Бонус за продажу аксессуаров
        "bonus_motivation": int,          # Бонус за мотивацию
        "plan_motivation_prod": int,      # План мотивации продаж
        "sales_motivation_prod": int,     # Продажи мотивации продаж
        "bonus_motivation_prod": int,     # Бонус за мотивацию продаж
        "salary": int,                   # Заработная плата
        "surcharge": int,                # Надбавка
        "total_salary": int,             # Общая заработная плата
        "closeDate": until_[:10]         # Дата окончания периода (обрезанная до дня)
    }
    """
    # Инициализируем пустой словарь, в который будем добавлять информацию о заработке сотрудника
    result = {}
    # Получаем информацию о заработной плате с помощью различных функций
    result.update(get_aks_salary(shop_id, since_, until_))
    result.update(get_mot_salary(shop_id, since_, until_))
    result.update(get_plan_bonus(shop_id, since_, until_))
    result.update(get_salary(shop_id, until_))
    result.update(get_surcharge(employee_uuid, until_))
    # Добавляем дату окончания периода в результат (обрезанную до дня)
    result.update({"closeDate": until_[:10]})
    # Вычисляем общую заработную плату
    total_salary = (
        result["bonus_accessory"]
        + result["bonus_motivation"]
        + result["bonus_motivation_prod"]
        + result["salary"]
        + result["surcharge"]
    )
    # Добавляем общую заработную плату в результат
    result.update({"total_salary": total_salary})
    # Возвращаем словарь result с информацией о заработке сотрудника
    return result


def diagram(data: dict) -> BytesIO:
    """
    Создает круговую диаграмму на основе данных из словаря и возвращает изображение в формате BytesIO.
    Args:
        data: dict - Входные данные в виде словаря, где ключи - названия, а значения - суммы.

    Return: BytesIO - Объект BytesIO с изображением.
    """

    # Извлекаем ключи (названия) и значения (суммы) из словаря данных
    name = list(data.keys())
    sum = list(data.values())

    # Создаем новую фигуру (график) для диаграммы с заданными размерами
    plt.figure(figsize=(10, 10))

    # Устанавливаем размер шрифта для процентных значений на диаграмме
    plt.rcParams["font.size"] = 14  # Здесь задайте желаемый размер шрифта

    # Создаем круговую диаграмму с указанными данными и параметрами
    plt.pie(
        sum,
        labels=name,
        autopct="%1.1f%%",  # Формат для отображения процентов на диаграмме
        startangle=140,  # Угол начала отрисовки диаграммы
        textprops={"fontweight": "bold"},  # Свойства текста (жирный шрифт)
    )

    # Задаем равное соотношение сторон для круга
    plt.axis("equal")

    # Создаем объект BytesIO для сохранения изображения в памяти
    image_buffer = BytesIO()

    # Сохраняем диаграмму в объект BytesIO в формате PNG
    plt.savefig(image_buffer, format="png")

    # Очищаем буфер изображения и перемещаем указатель в начало
    image_buffer.seek(0)

    # Закрываем текущий график, чтобы он не отображался
    plt.close()

    # Возвращаем объект BytesIO с изображением
    return image_buffer


# Функция для сбора статистики по продажам {uuid: commodity}
def gather_statistics_uuid(documents, products_uuid):
    """
    Собирает статистику по продажам для каждого товара в заданных документах.

    Parameters:
    - documents: Список документов продажи
    - products_uuid: Список UUID товаров

    Returns:
    - data_sale: Словарь с количеством проданных товаров для каждого UUID товара
    """
    data_sale = {}
    for doc in documents:
        for trans in doc["transactions"]:
            if trans["x_type"] == "REGISTER_POSITION":
                if trans["commodityUuid"] in products_uuid:
                    if trans["commodityUuid"] in data_sale:
                        data_sale[trans["commodityUuid"]] += trans["quantity"]
                    else:
                        data_sale[trans["commodityUuid"]] = trans["quantity"]
    return data_sale


# Функция для сбора статистики по продажам {name: commodity}
def gather_statistics_name(documents, products_uuid):
    """
    Собирает статистику по продажам для каждого товара в заданных документах.

    Parameters:
    - documents: Список документов продажи
    - products_uuid: Список UUID товаров

    Returns:
    - data_sale: Словарь с количеством проданных товаров для каждого UUID товара
    """
    data_sale = {}
    for doc in documents:
        for trans in doc["transactions"]:
            if trans["x_type"] == "REGISTER_POSITION":
                if trans["commodityUuid"] in products_uuid:
                    if trans["commodityName"] in data_sale:
                        data_sale[trans["commodityName"]] += trans["quantity"]
                    else:
                        data_sale[trans["commodityName"]] = trans["quantity"]
    return data_sale


def cash() -> int:
    sum_ = 0
    cash = CashRegister.objects()

    if cash:
        for doc in cash:
            pprint(doc["cash"])
            if doc["x_type"] == "CASH_INCOME":
                sum_ += int(doc["cash"])

            if doc["x_type"] == "CASH_OUTCOME":
                sum_ -= int(doc["cash"])

        return sum_
    else:
        return sum_


def last_time(shop_id: str) -> dict[str:str]:
    # Определение временного периода для анализа
    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().isoformat()

    shop = Shop.objects(uuid__exact=shop_id).only("name").first()
    pprint(shop["name"])
    Documents_last_time = (
        Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": shop_id,
            }
        )
        .order_by("-closeDate")
        .only("closeDate")
        .first()
    )
    if Documents_last_time:
        time = get(Documents_last_time.closeDate).shift(hours=3).isoformat()[11:19]
    else:
        time = 0

    pprint(time)
    return {f"🕰️ выг. {shop.name}": time}


def sale_uuid(shop_id: list[str], since: str, until: str) -> list:
    documents = Documents.objects(
        __raw__={
            "closeDate": {"$gte": since, "$lt": until},
            "shop_id": {"$in": shop_id},
            "x_type": "SELL",
        }
    )
