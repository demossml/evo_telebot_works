from bd.model import (
    Session,
    Products,
)
import json


from evotor.evotor import evo


from io import BytesIO

name = "Отчет 3_1".upper()
desc = ""
mime = "json"


def get_inputs(session: Session):
    return {}


def generate(session: Session):

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

    result = []

    # Получаем продукты для магазина и группы товаров
    products = Products.objects(
        __raw__={
            "shop_id": "20191117-BF71-40FE-8016-1E7E4A3A4780",
            "parentUuid": {"$in": group_id},
        }
    )
    for item in products:
        result.append(
            {
                "uuid": item.uuid,
                "group": item.group,
                "parentUuid": item.parentUuid,
            }
        )

    print("Данные успешно сформированы:", result)

    # Преобразуем результат в JSON строку
    print("Преобразование данных в JSON...")
    json_result = json.dumps(result, ensure_ascii=False, indent=4)

    # Создаем объект BytesIO для работы с байтами
    json_bytes = json_result.encode("utf-8")
    byte_stream = BytesIO(json_bytes)
    byte_stream.name = "report.json"  # Задаем имя для файла
    byte_stream.seek(0)

    print("Файл JSON успешно сгенерирован. Размер файла:", len(byte_stream.getvalue()))

    # Возвращаем объект BytesIO, который можно будет отправить как файл
    return byte_stream
