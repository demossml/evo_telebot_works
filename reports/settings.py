from bd.model import (
    Session,
    Status,
    Documents,
    Shift_Opening_Report,
    Employees,
    Shop,
    Products,
    ZReopt,
    GetTime,
    Surplus,
    GroupUuidAks,
    Plan,
    Сonsent,
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
    ReportsOperatingModeShopInput,
)

from .util import get_period, generate_plan_parallel, get_shops_uuid_user_id

import sys

import logging

logger = logging.getLogger(__name__)

from pprint import pprint

name = "🛠 Настройки ➡️".upper()
desc = ""
mime = "text"


class СloseDateInput:
    desc = "Напишите время открытия ТТ в формате ч:м (00:00)✍️".upper()
    type = "MESSAGE"


class OpenDateInput:
    desc = "Напишите время закрытие ТТ в формате ч:м (00:00)✍️".upper()
    type = "MESSAGE"


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
            return {
                "shop": ShopInput,
                "docStatus": DocStatusInput,
            }
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

    elif report_type == "operating_mode":
        if not report_type_d:
            return {"report_d": ReportsOperatingModeShopInput}
        if report_type_d == "operating_shops":
            return {
                "shop": ShopInput,
                "openDate": OpenDateInput,
                "closeDate": СloseDateInput,
                "docStatus": DocStatusInput,
            }
        elif report_type_d == "get_operating_shops":
            return {}
    elif report_type == "openData":
        return {}
    elif report_type == "32Fm":
        return {}


def generate(session: Session):
    inputs = session.params.get("inputs", {}).get("0", {})
    pprint(inputs)
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

    elif report_type_d == "restore_shops":
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

    elif report_type_d == "delete_employees":
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

    elif report_type_d == "restore_employees":
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
            Status.objects(employee=employee_uuid).update(**data_params, upsert=True)

            report_data.append({"employee": employee.name, "status": "restore"})
        return report_data

    elif report_type == "clean_up_the_database":
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
            "clear_db_status": Status,
        }
        clear_collection_name = session.params["inputs"]["0"]["collection_name"]

        clear_collection = collection[clear_collection_name]

        clear_collection.drop_collection()

        return [{"Коллекция": "Очищена"}]

    elif report_type == "plan_generation":

        # Получение начальной и конечной дат периода
        since = session.params["inputs"]["0"]["openDate"]
        until = session.params["inputs"]["0"]["closeDate"]

        shops_id = get_shops_uuid_user_id(session)

        return generate_plan_parallel(shops_id, since, until)

    elif report_type == "openData":
        logger.info("openData")
        try:
            for doc in Shift_Opening_Report.objects(locationData__exists=True):
                Shift_Opening_Report.objects(id=doc.id).update(
                    set__openData=doc.locationData, unset__locationData=1
                )

            return [{"1": 1}]
        except Exception as e:
            logger.info(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

    elif report_type == "32Fm":
        consent = Сonsent.objects()

        for item in consent:
            if "status" not in item:
                params = {"status": "activ"}

                Сonsent.objects(user_id=item["user_id"]).update(**params, upsert=True)

        return [{"status": "activ"}]

    elif report_type_d == "operating_shops":
        report_data = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(room) + 1):
            # Добавляем "shop_id" в список shop_ids
            shop_id = session.params["inputs"][str(i)]["shop"]
            shop = Shop.objects(uuid=shop_id).first()

            openDate = session.params["inputs"][str(i)]["openDate"]
            closeDate = session.params["inputs"][str(i)]["closeDate"]

            data_params = {
                "x_type": "OPERATING_SHOPS",
                "shop": shop_id,
                "openDate": openDate,
                "closeDate": closeDate,
            }
            Status.objects(shop=shop_id, x_type="OPERATING_SHOPS").update(
                **data_params, upsert=True
            )

            report_data.append(
                {
                    "shop": shop.name,
                    "openDate": openDate,
                    "closeDate": closeDate,
                }
            )
        return report_data

    elif report_type_d == "get_operating_shops":
        report_data = []

        documents = Status.objects(x_type="OPERATING_SHOPS")

        for doc in documents:
            shop = Shop.objects(uuid=doc["shop"]).only("name").first().name
            report_data.append(
                {
                    "ТТ": shop,
                    "openDate": doc.openDate,
                    "closeDate": doc.closeDate,
                }
            )
        return report_data
