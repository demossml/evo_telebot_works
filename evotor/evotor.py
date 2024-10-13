"""
Evotor Client
"""

import requests
from arrow import get, utcnow
from pprint import pprint


# URL запросов к APIv1
# https://api.evotor.ru/api/v1/inventories/employees/search"


# Класс для взаимодействия с API Evotor
class Evotor:
    def __init__(self, token: str):
        # Инициализация объекта Evotor с переданным токеном
        self.token = token
        self.headers = {"X-Authorization": token}
        # URL для получения списка сотрудников
        self.get_employees_url = (
            "https://api.evotor.ru/api/v1/inventories/employees/search"
        )
        # URL для получения списка магазинов
        self.get_shops_url = "https://api.evotor.ru/api/v1/inventories/stores/search"
        # URL для получения списка продуктов в магазине
        self.get_products_url = (
            "https://api.evotor.ru/api/v1/inventories/stores/{}/products"
        )
        # URL для получения документов Z-отчетов
        self.get_z_report_url = "https://api.evotor.ru/api/v1/inventories/stores/{}/documents?gtCloseDate={}&ltCloseDate={}&types=FPRINT"
        # URL для получения документов выплат
        self.get_cash_outcome_url = "https://api.evotor.ru/api/v1/inventories/stores/{}/documents?gtCloseDate={}&ltCloseDate={}&types=CASH_OUTCOME"
        # URL для получения документов продаж
        self.get_sell_url = "https://api.evotor.ru/api/v1/inventories/stores/{}/documents?gtCloseDate={}&ltCloseDate={}&types=SELL"
        # URL для получения всех документов
        self.get_doc_url = "https://api.evotor.ru/api/v1/inventories/stores/{}/documents?gtCloseDate={}&ltCloseDate={}"

    def get_sell_documents(self, shop_id: str, since: str, until: str) -> list:
        """
        Получает документы типа SELL (продажи) для данного магазина в указанный диапазон дат.
        :param shop_id: Идентификатор магазина
        :param since: Начальная дата (в формате ISO)
        :param until: Конечная дата (в формате ISO)
        :return: Список документов
        """
        # Формирование URL с параметрами дат и идентификатором магазина
        url = self.get_sell_url.format(shop_id, since, until)

        # Получение документов
        response = requests.get(url, headers=self.headers)
        if response.ok:
            documents = response.json()
            # print(documents)

            # Фильтруем документы по полю x_type = "SELL"
            filtered_documents = [doc for doc in documents if doc.get("type") == "SELL"]
            return filtered_documents
        return []

    def get_first_open_session(
        self, shops_id: list[str], since: str, until: str, user_uuid: str
    ) -> dict:
        """Проходит по всем shop_id, получает первый документ с типом 'OPEN_SESSION' для каждого магазина и возвращает его, либо None."""

        # Проходим по каждому shop_id в списке
        for shop_id in shops_id:
            # pprint(f"shop: {shop_id}")
            # Формируем URL для запроса
            url = self.get_doc_url.format(shop_id, since, until)

            # Получаем данные о документах для текущего магазина
            response = requests.get(url, headers=self.headers)

            # Проверка успешности запроса
            if response.ok:
                documents = response.json()
                # pprint(user_uuid)

                # Поиск первого документа с типом 'OPEN_SESSION' и UUID пользователя
                for doc in documents:

                    if (
                        doc.get("type") == "OPEN_SESSION"
                        and doc.get("openUserUuid") == user_uuid
                    ):
                        return doc  # Возвращаем первый найденный документ
            else:
                # Логируем ошибку запроса (можно добавить обработку ошибок)
                print(
                    f"Ошибка при запросе данных для магазина {shop_id}: {response.status_code}"
                )

        # Если ничего не найдено, возвращаем None
        return None

    #  метод для получения документов о продажах и возвратах
    def get_documents_by_products(self, shop_id: str, since: str, until: str) -> dict:
        """Получает документы о продажах и возвратах для указанных продуктов"""
        # Формируем URL для запроса
        url = self.get_sell_url.format(shop_id, since, until)

        # Получаем данные о документах
        response = requests.get(url, headers=self.headers)

        # Проверка успешности запроса
        if response.ok:
            documents = response.json()

            # Фильтруем документы по типам операций и products_uuid
            filtered_documents = [
                doc
                for doc in documents
                if doc["type"] in ("SELL", "PAYBACK")  # Фильтр по типам
            ]

            return filtered_documents
        else:
            # Возвращаем пустой список или выбрасываем исключение в зависимости от ситуации
            return []

    def get_shops(self) -> dict:
        """Получает данные магазинов"""
        return requests.get(self.get_shops_url, headers=self.headers).json()

    def get_shop_name(self, shop_uuid: str) -> str:
        """Получает имя магазина по его UUID."""
        # Получаем данные о всех магазинах
        shops = self.get_shops()

        # Проходим по каждому магазину и ищем по UUID
        for shop in shops:
            if shop.get("uuid") == shop_uuid:
                return shop.get(
                    "name", "Имя магазина не найдено"
                )  # Возвращаем имя или сообщение о том, что не найдено

        # Если ничего не найдено, возвращаем сообщение
        return "Магазин с данным UUID не найден"

    def get_shops_uuid(self) -> list[str]:
        """Получает список UUID магазинов"""

        # Выполняем запрос на получение данных магазинов
        response = requests.get(self.get_shops_url, headers=self.headers)

        # Проверка успешности запроса
        if response.ok:
            # Извлекаем данные магазинов
            shops = response.json()
            # pprint(shops)
            # Извлекаем список uuid магазинов
            shop_uuids = [shop.get("uuid") for shop in shops if "uuid" in shop]

            return shop_uuids
        else:
            # В случае ошибки возвращаем пустой список или можно обработать исключение
            return []

    def get_employees(self) -> dict:
        """Получает данные магазинов сотрудников"""
        return requests.get(self.get_employees_url, headers=self.headers).json()

    def get_products(self, shop_id: str) -> dict:
        """Получает данные  продуктов"""
        url = self.get_products_url.format(shop_id)
        products = requests.get(url, headers=self.headers).json()
        return products

    def get_groups(self, shop_id: str) -> dict:
        """Получает данные групп продуктов"""
        url = self.get_products_url.format(shop_id)
        products = requests.get(url, headers=self.headers).json()
        return list(filter(lambda x: x["group"] is True, products))

    def get_products_by_group(
        self,
        shop_id: str,
        group_ids: tuple,
    ) -> list:
        """Получает идентификаторы продуктов по заданным группам товаров и времени"""
        # Получаем список продуктов
        products = self.get_products(shop_id)
        # Формируем список идентификаторов продуктов, относящихся к заданным группам
        products_uuid = [
            product["uuid"]
            for product in products
            if product["parentUuid"] in group_ids
        ]
        return products_uuid

    def get_z_report(self, shop_id: str, gtCloseDate, ltCloseDate) -> dict:
        """Получает документы z отчетов"""
        url = self.get_z_report_url.format(shop_id, gtCloseDate, ltCloseDate)
        return requests.get(url, headers=self.headers).json()

    def get_cash_outcome(self, shop_id: str, gtCloseDate, ltCloseDate) -> dict:
        """Получает документы выплат"""
        url = self.get_cash_outcome_url.format(shop_id, gtCloseDate, ltCloseDate)
        return requests.get(url, headers=self.headers).json()

    def get_sell(self, shop_id: str, gtCloseDate, ltCloseDate) -> dict:
        """Получает документы продаж"""
        url = self.get_sell_url.format(shop_id, gtCloseDate, ltCloseDate)
        return requests.get(url, headers=self.headers).json()

    def get_doc(self, shop_id: str, gtCloseDate, ltCloseDate) -> dict:
        """Получает документы"""
        url = self.get_doc_url.format(shop_id, gtCloseDate, ltCloseDate)
        return requests.get(url, headers=self.headers).json()

    def get_response(self) -> bool:
        """Получает True или False"""
        return requests.get(self.get_shops_url, headers=self.headers).ok

    def get_last_z_report(self, shop_id: str, gtCloseDate, ltCloseDate) -> dict:
        """
        Получает последний документ типа FPRINT_Z_REPORT для данного магазина
        """
        url = self.get_z_report_url.format(shop_id, gtCloseDate, ltCloseDate)
        z_reports = requests.get(url, headers=self.headers).json()

        if not z_reports:
            return {"message": "No Z-reports found"}

        # Сортируем по дате закрытия и берем последний документ
        last_z_report = max(z_reports, key=lambda report: report.get("closeDate", ""))
        return last_z_report

    def get_last_z_report_today(self, shop_id: str) -> dict:
        """Получает последний документ типа FPRINT_Z_REPORT за текущий день"""
        # Текущая дата в локальном времени, начало и конец дня
        today_start = (
            utcnow().to("local").replace(hour=0, minute=0, second=0).isoformat()
        )
        today_end = (
            utcnow().to("local").replace(hour=23, minute=59, second=59).isoformat()
        )

        # Формируем URL для поиска Z-отчетов за сегодня
        url = self.get_z_report_url.format(shop_id, today_start, today_end)
        response = requests.get(url, headers=self.headers)

        # Проверка успешности запроса и возврат последнего документа, если он есть
        if response.ok:
            reports = response.json()
            if reports:
                return reports[-1]  # Возвращаем последний документ
            return {"message": "Z-отчеты не найдены за сегодняшний день"}
        else:
            return {"error": "Не удалось получить Z-отчеты"}


evo = Evotor("1126f94c-2b19-490e-872c-49ded3be310e")
