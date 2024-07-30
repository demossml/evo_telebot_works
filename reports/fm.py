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

from .inputs import FmSettingsInput, ShopAllInput, PeriodDateInput

name = "FM"
desc = "З"
mime = "text"


class CollectionsInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "shift", "name": "Shift_Opening_Report"},
            {"id": "zReopt", "name": "ZReopt"},
            {"id": "plan", "name": "Plan"},
            {"id": "marriageWarehouse", "name": "MarriageWarehouse"},
        )

        return output


class FileInput:
    name = "Файл"
    desc = "Отправте файл в формате xlsx"
    type = "FILE"


def get_inputs(session: Session):
    inputs = session.params.get("inputs", {}).get("0", {})

    if not inputs:
        return {
            "report": FmSettingsInput,
        }

    report_type = inputs.get("report", None)

    if report_type == "download_data":
        return {"data": FileInput}

    elif report_type == "get_seles":
        return {
            "shop": ShopAllInput,
            "period": PeriodDateInput,
        }

    elif report_type == "stock_balances":
        return {
            "shop": ShopAllInput,
            "period": PeriodDateInput,
        }


def generate(session: Session):
    inputs = session.params.get("inputs", {}).get("0", {})
    report_type = inputs.get("report", None)

    if report_type == "download_data":

        return {"data": FileInput}

    elif report_type == "get_seles":
        pass

    elif report_type == "stock_balances":
        pass
