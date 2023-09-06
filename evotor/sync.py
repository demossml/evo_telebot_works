from evotor import Evotor
from config import (
    EVOTOR_TOKEN_5,
    EVOTOR_TOKEN_2,
    EVOTOR_TOKEN_3,
    EVOTOR_TOKEN_4,
    EVOTOR_TOKEN_8,
)
from util import get_intervals, prune
from bd.model import Shop, Products, Documents, Employees, Users
from pprint import pprint
from arrow import utcnow
import schedule
import time


# Сенхронизирует базу tc и облако эватор.
# Принимает два оргумента shop_id и evotor.


# Функция для синхронизации сотрудников
def sync_employees(evotor):
    # Итерируемся по сотрудникам из объекта evotor.
    for item in evotor.get_employees():
        # Создаем словарь с параметрами для обновления записей в базе данных.
        # Ключи в словаре формируются на основе ключей в объекте 'item'.
        # Например, если 'item' содержит ключ 'uuid', то ключ в словаре будет 'set__uuid'.
        params = {"set__" + k: v for k, v in item.items()}

        # Обновляем или добавляем записи в базе данных Employees.
        # Используется метод 'update' с условием, что 'uuid' сотрудника совпадает.
        # Если сотрудник с указанным 'uuid' уже существует, то его данные обновляются.
        # В противном случае, создается новая запись.
        Employees.objects(uuid=item["uuid"]).update(**params, upsert=True)


# Функция для синхронизации магазинов
def sync_shops(evotor):
    # Итерируемся по каждому магазину, полученному из evotor.get_shops()
    for item in evotor.get_shops():
        # Создаем словарь параметров для обновления в MongoDB
        # Ключи в этом словаре будут иметь вид "set__<ключ из item>"
        # и значения будут соответствовать значениям из item
        params = {"set__" + k: v for k, v in item.items()}

        # Выполняем обновление или вставку записи в коллекцию Shop в MongoDB
        # Используем UUID из item как идентификатор записи
        Shop.objects(uuid=item["uuid"]).update(**params, upsert=True)


# Функция для синхронизации продуктов
def sync_products(evotor, shop_id):
    # Получение продуктов из Evotor API для указанного магазина
    products = prune(evotor.get_products(shop_id))

    # Проверка, что есть продукты для обновления
    if products:
        # Итерируемся по каждому продукту в списке
        for item in products:
            # Создаем словарь с параметрами для обновления объекта в базе данных
            params = {"set__" + k: v for k, v in item.items()}
            # Добавляем в словарь параметр shop_id для указания магазина
            params["set__shop_id"] = shop_id

            # Выполняем обновление или вставку записи в коллекцию Products в MongoDB
            # Используем UUID из item как идентификатор записи
            Products.objects(uuid=item["uuid"], shop_id=shop_id).update(
                **params, upsert=True
            )


# Функция для синхронизации документов
def sync_docoments(evotor, shop_id):
    # Получает дату последнего документа из базы данных
    closedate_db = (
        Documents.objects(shop_id__exact=shop_id).order_by("-closeDate").first()
    )
    # Провиряет наличие даты последнего декумента
    if closedate_db:
        max_closed_date_from_database = closedate_db.closeDate
    else:
        max_closed_date_from_database = ""
    # функция max проверяет max_closed_date_from_database если пустая сторока то сеегодня минус три года
    # если max_closed_date_from_database не пустая строка (дата последнего документа) то остовляет ее
    star_date = max(
        utcnow().shift(months=-2).isoformat(), max_closed_date_from_database
    )

    finish_date = utcnow().isoformat()
    # Разбивает период на интервалы и получает документы за каждый интервал
    for left, right in get_intervals(star_date, finish_date, "days", 30):
        documents = evotor.get_doc(shop_id, gtCloseDate=left, ltCloseDate=right)
        if len(documents) > 4:
            for item in prune(documents):
                # Создаем словарь с параметрами для обновления объекта в базе данных
                params = {"set__" + k: v for k, v in item.items()}
                # Добавляем в словарь параметр shop_id для указания магазина
                params["set__shop_id"] = shop_id

                # Выполняем обновление или вставку записи в коллекцию Documents в MongoDB
                # Используем UUID из item как идентификатор записи
                Documents.objects(uuid=item["uuid"]).update(**params, upsert=True)


# Функция для синхронизации всей информации
def sync_total(evotor):
    # Синхронизация магазинов
    sync_shops(evotor)
    # Синхронизация сотрудников
    sync_employees(evotor)

    # Для каждого магазина в Evotor
    for shop in evotor.get_shops():
        # Выводим UUID магазина
        pprint(shop["uuid"])
        # Синхронизация продуктов для данного магазина
        sync_products(evotor, shop["uuid"])
        # Синхронизация документов для данного магазина
        sync_docoments(evotor, shop["uuid"])


# Функция для синхронизации всей информации для всех магазинов
def sync_all():
    sync_total(Evotor(EVOTOR_TOKEN_8))
    sync_total(Evotor(EVOTOR_TOKEN_2))
    sync_total(Evotor(EVOTOR_TOKEN_3))
    sync_total(Evotor(EVOTOR_TOKEN_4))
    sync_total(Evotor(EVOTOR_TOKEN_5))


# Вызов функции для начальной синхронизации
sync_all()

# Расписание для периодической синхронизации
schedule.every(550).seconds.do(sync_all)

# Бесконечный цикл для выполнения задач по расписанию
while True:
    schedule.run_pending()
    time.sleep(1)
