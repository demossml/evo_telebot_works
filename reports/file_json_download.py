import json
from pprint import pprint
from bd.model import (
    Session,
    Shift_Opening_Report,
    Plan,
    ZReopt,
    Plan,
    MarriageWarehouse,
)

name = "Загрузить данные"
desc = "Загружает данне из json в базу"
mime = "text"


class CollectionsInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "shift", "name": "Shift_Opening_Report"},
            {"id": "zReopt", "name": "ZReopt"},
            {"id": "plan", "name": "Plan"},
            {"id": "marriageWarehouse", "name": "MarriageWarehouse"},
        ]

        return output


class FileInput:
    name = "Файл"
    desc = "Отправте файл в формате json"
    type = "FILE"


def get_inputs(session: Session):
    return {"collection": CollectionsInput, "file": FileInput}


def add_collection(date_: str, collection: str):
    """Добавить данные из JSON-файла в указанную коллекцию MongoDB.

    Args:
        date_ (str): Путь к JSON-файлу, содержащему данные для добавления.
        collection (str): Название целевой коллекции MongoDB.

    Returns:
        None
    """
    # Словарь, который сопоставляет имена коллекций с соответствующими моделями
    collections = {
        "shift": Shift_Opening_Report,
        # "products": Products,
        # "car_list": Car_list,
        "zReopt": ZReopt,
        "plan": Plan,
        "marriageWarehouse": MarriageWarehouse,
    }

    # Преобразуйте JSON-текст в Python-структуру данных (список словарей)
    data = json.loads(date_)
    # Итерируемся по данным из файла JSON
    for items in data:
        params = {}

        # Итерируемся по ключам и значениям в элементах данных
        for k, v in items.items():
            if k != "_id":
                params.update({k: v})
        # В зависимости от выбранной коллекции выполняем обновление данных
        if collection == "shift":
            if type(params["user_id"]) == dict:
                for k, v in params["user_id"].items():
                    params["user_id"] = int(v)
            if "locationData" in params:
                collections[collection].objects(
                    locationData=params["locationData"]
                ).update(**params, upsert=True)
            else:
                collections[collection].objects(openData=params["openData"]).update(
                    **params, upsert=True
                )
        # if collection == "products":
        #     collections[collection].objects(uuid=params["uuid"]).update(
        #         **params, upsert=True
        #     )

        # if collection == "car_list":
        #     if type(params["user_id"]) == dict:
        #         for k, v in params["user_id"].items():
        #             params["user_id"] = int(v)
        #     collections[collection].objects(user_id=params["user_id"]).update(
        #         **params, upsert=True
        #     )

        if collection == "zReopt":
            if type(params["user_id"]) == dict:
                for k, v in params["user_id"].items():
                    params["user_id"] = int(v)
            collections[collection].objects(locationData=params["locationData"]).update(
                **params, upsert=True
            )

        if collection == "plan":
            collections[collection].objects(closeDate=params["closeDate"]).update(
                **params, upsert=True
            )

        if collection == "marriageWarehouse":
            if type(params["user_id"]) == dict:
                for k, v in params["user_id"].items():
                    params["user_id"] = int(v)
            collections[collection].objects(closeDate=params["closeDate"]).update(
                **params, upsert=True
            )


def generate(session: Session):
    params = session.params["inputs"]["0"]
    collection = params["collection"]

    add_collection(params["file"], collection)

    return [{"Ok": " "}]
