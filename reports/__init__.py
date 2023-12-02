# reports/__init__.py
from reports import settings
from reports import get_cash_report
from reports import get_commodity_reports
from reports import get_sales
from reports import shift_opening
from reports import get_electro_sales
from reports import get_electro_sales_plan
from reports import get_accept
from reports import get_leftovers
from reports import V1
from reports import salary
from reports import data_analysis
from reports import break_
from reports import sales_today
from reports import break_today
from reports import file_json_download
from reports import v2
from reports import V3_1

from bd.model import Session

user_id_di3 = [1254862309, 5640546945]


def get_reports(session: Session):
    # print(session.employee.role)
    if "role" in session.employee:
        if session.employee.role == "CASHIER":
            return {
                "get_cash_report": get_cash_report,
                "get_commodity_reports": get_commodity_reports,
                "get_sales": get_sales,
                "shift_opening": shift_opening,
                "get_electro_sales": get_electro_sales,
                "get_electro_sales_plan": get_electro_sales_plan,
                "break_": break_,
            }
        if session.employee.role == "ADMIN":
            return {
                "settings": settings,
                "salary": salary,
                "break_": break_,
                "data_analysis": data_analysis,
                "get_cash_report": get_cash_report,
                "get_commodity_reports": get_commodity_reports,
                "get_sales": get_sales,
                "shift_opening": shift_opening,
                "get_electro_sales": get_electro_sales,
                "get_electro_sales_plan": get_electro_sales_plan,
                "sales_today": sales_today,
                "break_today": break_today,
            }
    if session.user_id in user_id_di3:
        return {
            "get_accept": get_accept,
            "get_leftovers": get_leftovers,
            "V1": V1,
            "v2": v2,
            "V3_1": V3_1,
            # "file_json_download": file_json_download,
        }


# Регистрирует отчеты
reports = {
    "settings": settings,
    "get_cash_report": get_cash_report,
    "get_commodity_reports": get_commodity_reports,
    "get_sales": get_sales,
    "shift_opening": shift_opening,
    "get_electro_sales": get_electro_sales,
    "get_electro_sales_plan": get_electro_sales_plan,
    "get_accept": get_accept,
    "get_leftovers": get_leftovers,
    "V1": V1,
    "salary": salary,
    "data_analysis": data_analysis,
    "break_": break_,
    "sales_today": sales_today,
    "break_today": break_today,
    "file_json_download": file_json_download,
    "v2": v2,
    "V3_1": V3_1,
}
