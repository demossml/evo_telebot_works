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
)
from .inputs import (
    ReportsSettingsInput,
    ReportsClearDbInput,
    ReportsDeleteRestoreShopInput,
    ReportsDeleteRestoreEmployeesInput,
    ShopInput,
    EmployeesUuidInput,
    DocStatusInput,
)

from pprint import pprint

name = "🛠 Настройки ➡️".upper()
desc = ""
mime = "text"


def get_inputs(session: Session):
    # Если входные параметры сессии существуют
    if session.params["inputs"]["0"]:
        # Если тип отчета - "shift_opening_report"
        if session.params["inputs"]["0"]["report"] == "clear_db":
            return {"report": ReportsClearDbInput}
        if session.params["inputs"]["0"]["report"] == "delete_restore_shop":
            if "param" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["param"] == "delete_shops":
                    return {
                        "shop": ShopInput,
                        "docStatus": DocStatusInput,
                    }
                if session.params["inputs"]["0"]["param"] == "restore_shops":
                    return {
                        "shop": ShopInput,
                        "docStatus": DocStatusInput,
                    }

            else:
                return {"param": ReportsDeleteRestoreShopInput}
        if session.params["inputs"]["0"]["report"] == "delete_restore_employees":
            if "param" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["param"] == "delete_employees":
                    return {
                        "employee": EmployeesUuidInput,
                        "docStatus": DocStatusInput,
                    }
                if session.params["inputs"]["0"]["param"] == "restore_employees":
                    return {
                        "employee": EmployeesUuidInput,
                        "docStatus": DocStatusInput,
                    }

            else:
                return {"param": ReportsDeleteRestoreEmployeesInput}
        # if session.params["inputs"]["0"]["report"] == "delete_restore_shop":
        #     # print(session.params["inputs"]["0"]["report"])
        #     return {"report1": ReportsDeleteRestoreEmployeesInput}

    else:
        pprint("ReportsSettingsInput")
        return {
            "report": ReportsSettingsInput,
        }


def generate(session: Session):
    room = session["room"]
    if session.params["inputs"]["0"]["param"] == "delete_shops":
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

    if session.params["inputs"]["0"]["param"] == "restore_shops":
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

    if session.params["inputs"]["0"]["param"] == "delete_employees":
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

    if session.params["inputs"]["0"]["param"] == "restore_employees":
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
    # collection = {
    #     "clear_db_employees": Employees,
    #     "clear_db_shops": Shop,
    #     "clear_db_documents": Documents,
    #     "clear_db_products": Products,
    #     "clear_db_z_report": ZReopt,
    #     "clear_db_sesion": Session,
    #     "clear_db_get_time": GetTime,
    #     "clear_db_surplus": Surplus,
    #     "clear_db_group_uuid_aks": GroupUuidAks,
    # }
    # clear_collection_name = session.params["inputs"]["0"]["report"]

    # clear_collection = collection[clear_collection_name]

    # clear_collection.drop_collection()

    # return [{"Коллекция": "Очищена"}]
