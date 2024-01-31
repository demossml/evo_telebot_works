from evotor import Evotor
from config import EVOTOR_TOKEN_2, EVOTOR_TOKEN_4, EVOTOR_TOKEN_5
from util import get_intervals, prune
from bd.model import Shop, Products, Documents, Employees, Users, TimeSync
from pprint import pprint
from arrow import utcnow
import schedule
import time
from threading import Thread, Event
import asyncio


# Сенхронизирует базу tc и облако эватор.
# Принимает два оргумента shop_id и evotor.


class EvoSync:
    def __init__(self, token: str):
        # Инициализация объекта Evotor с переданным токеном
        self.token = token
        self.evotor = Evotor(token)

    # Функция для синхронизации сотрудников
    def sync_employees(self):
        # Итерируемся по сотрудникам из объекта evotor.
        for item in self.evotor.get_employees():
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
    def sync_shops(self):
        # Итерируемся по каждому магазину, полученному из evotor.get_shops()
        for item in self.evotor.get_shops():
            # Создаем словарь параметров для обновления в MongoDB
            # Ключи в этом словаре будут иметь вид "set__<ключ из item>"
            # и значения будут соответствовать значениям из item
            params = {"set__" + k: v for k, v in item.items()}

            # Выполняем обновление или вставку записи в коллекцию Shop в MongoDB
            # Используем UUID из item как идентификатор записи
            Shop.objects(uuid=item["uuid"]).update(**params, upsert=True)

    # Функция для синхронизации продуктов
    def sync_products(self, shop_id):
        # Получение продуктов из Evotor API для указанного магазина
        products = prune(self.evotor.get_products(shop_id))

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
    def sync_docoments(self, shop_id):
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
            documents = self.evotor.get_doc(
                shop_id, gtCloseDate=left, ltCloseDate=right
            )
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
    def sync_total(self):
        # Синхронизация магазинов
        self.sync_shops()
        # Синхронизация сотрудников
        self.sync_employees()

        # Для каждого магазина в Evotor
        for shop in self.evotor.get_shops():
            # Выводим UUID магазина
            pprint(shop["uuid"])
            # Синхронизация продуктов для данного магазина
            self.sync_products(shop["uuid"])
            # Синхронизация документов для данного магазина
            self.sync_docoments(shop["uuid"])
            params = {
                "shop": shop["uuid"],
                "time": utcnow().shift(hours=3).isoformat()[11:19],
            }
            TimeSync.objects(shop=shop["uuid"]).update(**params, upsert=True)


async def sync_evo(event):
    start_time = time.time()
    print(
        f"Start функции sync_evo: {time.strftime('%H:%M:%S', time.localtime(start_time))} "
    )
    evo_1 = EvoSync(EVOTOR_TOKEN_2)
    evo_1.sync_total()
    evo_2 = EvoSync(EVOTOR_TOKEN_4)
    evo_2.sync_total()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения функции sync_evo: {execution_time:.2f} секунд")
    event.set()


async def main():
    event = Event()

    task = asyncio.create_task(sync_evo(event))

    await asyncio.gather(task)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

# # Функция для синхронизации всей информации для всех магазинов
# def sync_evo_1():
#     evo = EvoSync(EVOTOR_TOKEN_2)
#     # Засекаем время начала выполнения
#     start_time = time.time()
#     print(f"Start функции sync_evo_1: {start_time} секунд")
#     evo.sync_total()
#     # sync_total(Evotor(EVOTOR_TOKEN_4))
#     # sync_total(Evotor(EVOTOR_TOKEN_5))

#     # Рассчитываем время выполнения и выводим в консоль
#     end_time = time.time()
#     execution_time = end_time - start_time
#     print(f"Время выполнения функции sync_evo_1: {execution_time:.2f} секунд")
#     sync_evo_1()


# def sync_evo_2():
#     evo = EvoSync(EVOTOR_TOKEN_4)
#     # Засекаем время начала выполнения
#     start_time = time.time()
#     print(f"Start функции sync_evo_: {start_time} секунд")

#     # sync_total(Evotor(EVOTOR_TOKEN_2))
#     evo.sync_total()

#     # Рассчитываем время выполнения и выводим в консоль
#     end_time = time.time()
#     execution_time = end_time - start_time
#     print(
#         f"Время выполнения фуsync_evo_2 нкции sync_evo_2: {execution_time:.2f} секунд"
#     )
#     sync_evo_2()


# th1 = Thread(target=sync_evo_1)
# th1.start()

# th2 = Thread(target=sync_evo_2)
# th2.start()
