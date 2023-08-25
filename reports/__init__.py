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

from bd.model import Session

user_id_di3 = [1254862309, 5640546945]


def get_reports(session: Session):
    # print(session.employee.role)
    if 'role' in session.employee:
        if session.employee.role == "CASHIER":
            return {
                'get_cash_report': get_cash_report,
                'get_commodity_reports': get_commodity_reports,
                'get_sales': get_sales,
                'shift_opening': shift_opening,
                'get_electro_sales': get_electro_sales,
                'get_electro_sales_plan': get_electro_sales_plan
            }
        if session.employee.role == "ADMIN":
            return {
                'get_cash_report': get_cash_report,
                'get_commodity_reports': get_commodity_reports,
                'get_sales': get_sales,
                'shift_opening': shift_opening,
                'get_electro_sales': get_electro_sales,
                'get_electro_sales_plan': get_electro_sales_plan,
                'salary': salary

            }
    if session.user_id in user_id_di3:
        return {
            'get_accept': get_accept,
            'get_leftovers': get_leftovers,
            'V1': V1,
        }


# Регистрирует отчеты
reports = {
    'settings': settings,
    'get_cash_report': get_cash_report,
    'get_commodity_reports': get_commodity_reports,
    'get_sales': get_sales,
    'shift_opening': shift_opening,
    'get_electro_sales': get_electro_sales,
    'get_electro_sales_plan': get_electro_sales_plan,
    'get_accept': get_accept,
    'get_leftovers': get_leftovers,
    'V1': V1,
    'salary': salary

}
