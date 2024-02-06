"""
Evotor Client
"""

import requests


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

    def get_shops(self) -> dict:
        """Получает данные магазинов"""
        return requests.get(self.get_shops_url, headers=self.headers).json()

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
