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
    get_contact_information,
    get_personal_information,
    get_family_status,
    get_relatives_information,
    get_work_experience,
    get_education,
    more_info,
    get_questionnaire,
    fm,
    V3_1,
)


from bd.model import Session, Status
import sys
import logging

logger = logging.getLogger(__name__)

ids = [5700958253, 111]


def get_reports(session: Session):
    try:
        doc_status = Status.objects(user_id=str(session.user_id)).first()
        if doc_status:
            if doc_status["status"] == "restore":
                status = "yes"
            else:
                status = "no"
        else:
            status = "yes"
        print(status)
        if session.employee is not None and hasattr(session.employee, "role"):
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
                        "fm": fm,
                        "get_questionnaire": get_questionnaire,
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
                        "V3_1": V3_1,
                    }
        else:
            return {
                "get_personal_information": get_personal_information,
                "get_contact_information": get_contact_information,
                "get_family_status": get_family_status,
                "get_relatives_information": get_relatives_information,
                "get_work_experience": get_work_experience,
                "get_education": get_education,
                "more_info": more_info,
                # "balances": balances,
                # "cash_balance_in_tt": cash_balance_in_tt,
                # "cash_balance": cash_balance,
                # "cash_flow": cash_flow,
                # "cash_outcome": cash_outcome,
                # "сash_Income": сash_Income,
            }
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")


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
    "get_personal_information": get_personal_information,
    "get_contact_information": get_contact_information,
    "get_family_status": get_family_status,
    "get_relatives_information": get_relatives_information,
    "get_work_experience": get_work_experience,
    "get_education": get_education,
    "more_info": more_info,
    "get_questionnaire": get_questionnaire,
    "fm": fm,
    "V3_1": V3_1,
}
