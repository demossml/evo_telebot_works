"""
Evotor Client
"""
import requests


# URL запросов к APIv1
# https://api.evotor.ru/api/v1/inventories/employees/search"

class Evotor:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"X-Authorization": token}
        self.get_employees_url = (
            "https://api.evotor.ru/api/v1/inventories/employees/search"
        )
        self.get_shops_url = "https://api.evotor.ru/api/v1/inventories/stores/search"
        self.get_products_url = (
            "https://api.evotor.ru/api/v1/inventories/stores/{}/products"
        )
        self.get_z_report_url = "https://api.evotor.ru/api/v1/inventories/stores/{}/documents?gtCloseDate={}&ltCloseDate={}&types=FPRINT"
        self.get_cash_outcome_url = "https://api.evotor.ru/api/v1/inventories/stores/{}/documents?gtCloseDate={}&ltCloseDate={}&types=CASH_OUTCOME"
        self.get_sell_url = "https://api.evotor.ru/api/v1/inventories/stores/{}/documents?gtCloseDate={}&ltCloseDate={}&types=SELL"
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
        """Получает документы """
        url = self.get_doc_url.format(shop_id, gtCloseDate, ltCloseDate)
        return requests.get(url, headers=self.headers).json()

    def get_response(self) -> bool:
        """Получает True или False """
        return requests.get(self.get_shops_url, headers=self.headers).ok
