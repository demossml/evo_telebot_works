from evotor import Evotor
from config import EVOTOR_TOKEN, EVOTOR_TOKEN_5, EVOTOR_TOKEN_2, EVOTOR_TOKEN_3, EVOTOR_TOKEN_4, EVOTOR_TOKEN_8
from util import get_intervals, prune
from bd.model import Shop, Products, Documents, Employees, Users
from pprint import pprint
from arrow import utcnow
import schedule
import time


# Сенхронизирует базу tc и облако эватор.
# Принимает два оргумента shop_id и evotor.

def sync_employees(evotor):
    for item in evotor.get_employees():
        params = {"set__" + k: v for k, v in item.items()}
        Employees.objects(uuid=item["uuid"]).update(**params, upsert=True)


def sync_shops(evotor):
    for item in evotor.get_shops():
        params = {"set__" + k: v for k, v in item.items()}
        Shop.objects(uuid=item["uuid"]).update(**params, upsert=True)


def sync_products(evotor, shop_id):
    products = prune(evotor.get_products(shop_id))
    if products:
        for item in products:
            params = {"set__" + k: v for k, v in item.items()}
            params["set__shop_id"] = shop_id
            Products.objects(uuid=item["uuid"], shop_id=shop_id).update(
                **params, upsert=True
            )


# Сенхронизирует базу tc b облако эватор принимает один оргумент shop_id
def sync_docoments(evotor, shop_id):
    # Получает дату последнего длкумента
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
    star_date = max(utcnow().shift(months=-2).isoformat(), max_closed_date_from_database)

    finish_date = utcnow().isoformat()

    for left, right in get_intervals(star_date, finish_date, "days", 30):
        documents = evotor.get_doc(shop_id, gtCloseDate=left, ltCloseDate=right)
        if len(documents) > 4:
            for item in prune(documents):
                params = {"set__" + k: v for k, v in item.items()}
                params["set__shop_id"] = shop_id
                Documents.objects(uuid=item["uuid"]).update(**params, upsert=True)


def sync_total(evotor):
    sync_shops(evotor)
    sync_employees(evotor)

    for shop in evotor.get_shops():
        pprint(shop["uuid"])
        sync_products(evotor, shop["uuid"])
        sync_docoments(evotor, shop["uuid"])



def sync_all():
    sync_total(Evotor(EVOTOR_TOKEN_8))
    sync_total(Evotor(EVOTOR_TOKEN_2))
    sync_total(Evotor(EVOTOR_TOKEN_3))
    sync_total(Evotor(EVOTOR_TOKEN_4))
    sync_total(Evotor(EVOTOR_TOKEN_5))


sync_all()

schedule.every(550).seconds.do(sync_all)

while True:
    schedule.run_pending()
    time.sleep(1)
