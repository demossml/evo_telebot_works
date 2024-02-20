from bd.model import (
    Session,
    Status,
    Documents,
    Users,
    Employees,
    Shop,
    Products,
    ZReopt,
    GetTime,
    Surplus,
    GroupUuidAks,
    Plan,
)
from .inputs import (
    ReportsSettingsInput,
    ReportsClearDbInput,
    ReportsDeleteRestoreShopInput,
    ReportsDeleteRestoreEmployeesInput,
    ShopInput,
    EmployeesUuidInput,
    DocStatusInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
)

from .util import get_period, generate_plan_parallel, get_shops_uuid_user_id

from pprint import pprint

name = "🛠 Настройки ➡️".upper()
desc = ""
mime = "text"


def get_inputs(session: Session):
    inputs = session.params.get("inputs", {}).get("0", {})

    if not inputs:
        pprint(inputs)
        return {
            "report": ReportsSettingsInput,
        }

    report_type = inputs.get("report", None)
    report_type_d = inputs.get("report_d", None)

    if report_type == "clean_up_the_database":
        return {"collection_name": ReportsClearDbInput}

    elif report_type == "plan_generation":
        return {
            "period": PeriodDateInput,
            "openDate": OpenDatePastInput,
            "closeDate": CloseDatePastInput,
        }

    elif report_type == "delete_restore_shop":
        if not report_type_d:
            return {"report_d": ReportsDeleteRestoreShopInput}
        if report_type_d == "delete_shops":
            return {"report": ReportsClearDbInput}
        elif report_type_d == "restore_shops":
            return {
                "shop": ShopInput,
                "docStatus": DocStatusInput,
            }

    elif report_type == "delete_restore_employees":
        if not report_type_d:
            return {"report_d": ReportsDeleteRestoreEmployeesInput}

        elif report_type_d == "delete_employees":
            return {
                "employee": EmployeesUuidInput,
                "docStatus": DocStatusInput,
            }
        elif report_type_d == "delete_employees":
            return {
                "employee": EmployeesUuidInput,
                "docStatus": DocStatusInput,
            }

    # # Если входные параметры сессии существуют
    # if session.params["inputs"]["0"]:
    #     # Если тип отчета - "shift_opening_report"
    #     if session.params["inputs"]["0"]["report"] == "clear_db":
    #         return {"report": ReportsClearDbInput}
    #     if session.params["inputs"]["0"]["report"] == "delete_restore_shop":
    #         if "param" in session.params["inputs"]["0"]:
    #             if session.params["inputs"]["0"]["param"] == "delete_shops":
    #                 return {
    #                     "shop": ShopInput,
    #                     "docStatus": DocStatusInput,
    #                 }
    #             if session.params["inputs"]["0"]["param"] == "restore_shops":
    #                 return {
    #                     "shop": ShopInput,
    #                     "docStatus": DocStatusInput,
    #                 }

    #         else:
    #             return {"param": ReportsDeleteRestoreShopInput}
    #     if session.params["inputs"]["0"]["report"] == "delete_restore_employees":
    #         if "param" in session.params["inputs"]["0"]:
    #             if session.params["inputs"]["0"]["param"] == "delete_employees":
    #                 return {
    #                     "employee": EmployeesUuidInput,
    #                     "docStatus": DocStatusInput,
    #                 }
    #             if session.params["inputs"]["0"]["param"] == "restore_employees":
    #                 return {
    #                     "employee": EmployeesUuidInput,
    #                     "docStatus": DocStatusInput,
    #                 }

    #         else:
    #             return {"param": ReportsDeleteRestoreEmployeesInput}
    #     # if session.params["inputs"]["0"]["report"] == "delete_restore_shop":
    #     #     # print(session.params["inputs"]["0"]["report"])
    #     #     return {"report1": ReportsDeleteRestoreEmployeesInput}

    # else:
    #     pprint("ReportsSettingsInput")
    #     return {
    #         "report": ReportsSettingsInput,
    #     }


def generate(session: Session):
    inputs = session.params.get("inputs", {}).get("0", {})
    report_type = inputs.get("report", None)
    report_type_d = inputs.get("report_d", None)
    room = session["room"]
    if report_type_d == "delete_shops":
        report_data = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            # Добавляем "shop_id" в список shop_ids
            shop_id = session.params["inputs"][str(i)]["shop"]
            shop = Shop.objects(uuid=shop_id).first()

            data_params = {"x_type": "SHOP", "shop": shop_id, "status": "deleted"}
            Status.objects(shop=shop_id).update(**data_params, upsert=True)

            report_data.append({"shop": shop.name, "status": "deleted"})
        return report_data

    if report_type_d == "restore_shops":
        report_data = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            # Добавляем "shop_id" в список shop_ids
            shop_id = session.params["inputs"][str(i)]["shop"]
            shop = Shop.objects(uuid=shop_id).first()

            data_params = {"x_type": "SHOP", "shop": shop_id, "status": "restore"}
            Status.objects(shop=shop_id).update(**data_params, upsert=True)

            report_data.append({"shop": shop.name, "status": "restored"})
        return report_data

    if report_type_d == "delete_employees":
        report_data = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            # Добавляем "shop_id" в список shop_ids
            employee_uuid = session.params["inputs"][str(i)]["employee"]
            employee = Employees.objects(uuid=employee_uuid).first()

            data_params = {
                "x_type": "EMPLOYEE",
                "employee": employee_uuid,
                "user_id": employee["lastName"],
                "status": "deleted",
            }
            Status.objects(employee=employee_uuid).update(**data_params, upsert=True)

            report_data.append({"employee": employee.name, "status": "deleted"})
        return report_data

    if report_type_d == "restore_employees":
        report_data = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            # Добавляем "shop_id" в список shop_ids
            employee_uuid = session.params["inputs"][str(i)]["employee"]
            pprint(employee_uuid)
            employee = Employees.objects(uuid=employee_uuid).first()

            data_params = {
                "x_type": "EMPLOYEE",
                "employee": employee_uuid,
                "user_id": employee["lastName"],
                "status": "restore",
            }
            pprint(1)
            Status.objects(employee=employee_uuid).update(**data_params, upsert=True)
            pprint(2)

            report_data.append({"employee": employee.name, "status": "restore"})
        return report_data

    if report_type == "clean_up_the_database":
        collection = {
            "clear_db_employees": Employees,
            "clear_db_shops": Shop,
            "clear_db_documents": Documents,
            "clear_db_products": Products,
            "clear_db_z_report": ZReopt,
            "clear_db_sesion": Session,
            "clear_db_get_time": GetTime,
            "clear_db_surplus": Surplus,
            "clear_db_group_uuid_aks": GroupUuidAks,
            "clear_db_plan": Plan,
        }
        clear_collection_name = session.params["inputs"]["0"]["collection_name"]

        clear_collection = collection[clear_collection_name]

        clear_collection.drop_collection()

        return [{"Коллекция": "Очищена"}]

    if report_type == "plan_generation":

        # Получение начальной и конечной дат периода
        since = session.params["inputs"]["0"]["openDate"]
        until = session.params["inputs"]["0"]["closeDate"]

        shops_id = get_shops_uuid_user_id(session)

        return generate_plan_parallel(shops_id, since, until)
