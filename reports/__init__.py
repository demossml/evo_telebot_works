# reports/__init__.py
from reports import (
    settings,
    get_cash_report,
    get_commodity_reports,
    get_sales,
    shift_opening,
    get_electro_sales,
    get_electro_sales_plan,
    get_accept,
    get_leftovers,
    salary,
    data_analysis,
    break_,
    sales_today,
    break_today,
    file_json_download,
    get_salary_today,
)


from bd.model import Session


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
                "get_salary_today": get_salary_today,
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
                "get_salary_today": get_salary_today,
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
    "salary": salary,
    "data_analysis": data_analysis,
    "break_": break_,
    "sales_today": sales_today,
    "break_today": break_today,
    "file_json_download": file_json_download,
    "get_salary_today": get_salary_today,
}
