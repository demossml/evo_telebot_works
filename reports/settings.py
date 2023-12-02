from bd.model import Session, Documents, Users, Employees, Shop, Products
from .inputs import ReportsSettingsInput, ReportsClearDbInput

name = "🛠 Настройки ➡️".upper()
desc = ""
mime = "text"


def get_inputs(session: Session):
    # Если входные параметры сессии существуют
    if session.params["inputs"]["0"]:
        # Если тип отчета - "shift_opening_report"
        if session.params["inputs"]["0"]["report"] == "clear_db":
            return {"clear": ReportsClearDbInput}

    else:
        return {
            "report": ReportsSettingsInput,
        }


def generate(session: Session):
    params = {}
    collection = {
        "clear_db_employees": Employees,
        "clear_db_shops": Shop,
        "clear_db_documents": Documents,
        "clear_db_products": Products,
    }
    clear_collection_name = session.params["inputs"]["0"]["clear"]

    clear_collection = collection[clear_collection_name]

    clear_collection.drop_collection()

    return [{"Коллекция": "Очищена"}]
