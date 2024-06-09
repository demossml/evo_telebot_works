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
    cash_balance,
    cash_flow,
    cash_outcome,
    сash_Income,
    cash_balance_in_tt,
    cash_balance_in_tt_all,
    balances,
    get_for_product_liquidity,
)


from bd.model import Session, Status


ids = [5700958253, 111]


def get_reports(session: Session):
    doc_status = Status.objects(user_id=str(session.user_id)).first()
    if doc_status:
        if doc_status["status"] == "restore":
            status = "yes"
        else:
            status = "no"
    else:
        status = "yes"
    print(status)
    if "role" in session.employee:
        if status == "yes":
            if session.employee.role == "CASHIER":
                return {
                    "salary": salary,
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
            if status == "yes":
                return {
                    "settings": settings,
                    "salary": salary,
                    "break_": break_,
                    "cash_balance_in_tt_all": cash_balance_in_tt_all,
                    "data_analysis": data_analysis,
                    "get_cash_report": get_cash_report,
                    "get_commodity_reports": get_commodity_reports,
                    "get_sales": get_sales,
                    "shift_opening": shift_opening,
                    "get_electro_sales": get_electro_sales,
                    "get_electro_sales_plan": get_electro_sales_plan,
                    "get_salary_today": get_salary_today,
                    "sales_today": sales_today,
                    # "get_for_product_liquidity": get_for_product_liquidity,
                }
    if session.user_id in ids:
        return {
            "balances": balances,
            "cash_balance_in_tt": cash_balance_in_tt,
            "cash_balance": cash_balance,
            "cash_flow": cash_flow,
            "cash_outcome": cash_outcome,
            "сash_Income": сash_Income,
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
    "cash_balance": cash_balance,
    "cash_flow": cash_flow,
    "cash_outcome": cash_outcome,
    "сash_Income": сash_Income,
    "cash_balance_in_tt": cash_balance_in_tt,
    "cash_balance_in_tt_all": cash_balance_in_tt_all,
    "balances": balances,
    "get_for_product_liquidity": get_for_product_liquidity,
}
