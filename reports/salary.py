from bd.model import (
    Shop,
    Products,
    Documents,
    Session,
    Employees,
    GroupUuidAks,
    Plan,
    Document,
)
from .util import (
    get_shops_uuid_user_id,
    get_period,
    get_shops,
    get_intervals,
    get_total_salary,
    get_period_day,
    generate_plan,
)
from pprint import pprint
from collections import OrderedDict
import matplotlib.pyplot as plt
from .inputs import (
    GroupsInput,
    DocStatusInput,
    ReportSalaryInput,
    ReportsSalarySettingInput,
    ReportGroupUuidAccessoryInput,
    ShopInput,
    ReportMotivationUuidInput,
    GroupInput,
    ProductInput,
    ReportАssignSalaryInput,
    ReportMotivationInput,
    EmployeesInput,
    ReportSurchargeInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
)

from arrow import utcnow, get
import decimal
import concurrent.futures
from collections import defaultdict
from pprint import pprint


name = "🛒 Зарплата ➡️".upper()
desc = ""
mime = "text"


class MotivationInput:
    """
    Напишите сумму мотивации за выполнение плана ₱
    """

    desc = "Напишите сумму мотивации за выполнение плана ₱".upper()
    type = "MESSAGE"


class MotivationUuidInput:
    desc = "Напишите сумму мотивации ₱".upper()
    type = "MESSAGE"


class SalaryInput:
    desc = "Напишите оклад ₱".upper()
    type = "MESSAGE"


class EmployeesSurchargeInput:
    desc = "Напишите сумму доплаты ₱".upper()
    type = "MESSAGE"


def get_inputs(session: Session):
    # Периоды для запроса зарплатных данных
    period = ["day", "week", "fortnight", "month"]
    # Проверяем, есть ли данные о входах в сессии
    if session.params["inputs"]["0"]:
        # Настроить критерии расчета зарплат
        if session.params["inputs"]["0"]["reports"] == "setting":
            if "reports_salary-setting" in session.params["inputs"]["0"]:
                # Добавление и просмотр групп аксессуаров
                if (
                    session.params["inputs"]["0"]["reports_salary-setting"]
                    == "group_uuid_accessory"
                ):
                    if "report" in session.params["inputs"]["0"]:
                        # Назначить группы аксессуаров
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "assigning_group_uuid_accessory"
                        ):
                            return {
                                "parentUuid": GroupsInput,
                                "docStatus": DocStatusInput,
                            }
                        # Запрос назначенных групп аксессуаров
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "get_group_uuid_accessory"
                        ):
                            return {
                                "shop": ShopInput,
                            }
                    else:
                        return {"report": ReportGroupUuidAccessoryInput}
                # Добавление и просмотр мотивационого товара
                if (
                    session.params["inputs"]["0"]["reports_salary-setting"]
                    == "motivation_uuid_accessory"
                ):
                    if "report" in session.params["inputs"]["0"]:
                        # Назначить товар доб. мотивации
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "product_ext_motivation"
                        ):
                            if "parentUuid" in session.params["inputs"]["0"]:
                                # отдает список импутов
                                return {
                                    "uuid": ProductInput,
                                    "motivation": MotivationUuidInput,
                                    "docStatus": DocStatusInput,
                                }
                            else:
                                return {"parentUuid": GroupInput}
                        # Запрос назначенных товаров доб. мотивации
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "get_product_ext_motivation"
                        ):
                            return {
                                "shop": ShopInput,
                            }
                    else:
                        return {"report": ReportMotivationUuidInput}
                # Назначение и просмотр окладов на ТТ
                if (
                    session.params["inputs"]["0"]["reports_salary-setting"]
                    == "assigning_salary"
                ):
                    if "report" in session.params["inputs"]["0"]:
                        # Назначить оклады на ТТ
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "assigning_salary_"
                        ):
                            return {
                                "shop": ShopInput,
                                "salary": SalaryInput,
                                "docStatus": DocStatusInput,
                            }
                        # Запрос назначенных окладов
                        if session.params["inputs"]["0"]["report"] == "get_salary":
                            return {
                                "shop": ShopInput,
                            }
                    else:
                        return {"report": ReportАssignSalaryInput}
                # Назначение и просмотр суммы мотивации за вып. плана
                if (
                    session.params["inputs"]["0"]["reports_salary-setting"]
                    == "motivation"
                ):
                    if "report" in session.params["inputs"]["0"]:
                        # Назначить сум. за выпол. пл.
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "amount_of_motivation"
                        ):
                            return {
                                "shop": ShopInput,
                                "motivation": MotivationInput,
                                "docStatus": DocStatusInput,
                            }
                        # Запрос назначенной сум. за выпол. пл.
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "get_amount_of_motivation"
                        ):
                            return {"shop": ShopInput}
                    else:
                        return {"report": ReportMotivationInput}
                # Назначение и просмотр сум. доплату к зп.
                if (
                    session.params["inputs"]["0"]["reports_salary-setting"]
                    == "surcharge"
                ):
                    if "report" in session.params["inputs"]["0"]:
                        # Назначить доплату к зп
                        if (
                            session.params["inputs"]["0"]["report"]
                            == "assign_a_surcharge"
                        ):
                            return {
                                "uuid": EmployeesInput,
                                "surcharge": EmployeesSurchargeInput,
                                "docStatus": DocStatusInput,
                            }
                        # Запрос назначенной сум. доплатs к зп
                        if session.params["inputs"]["0"]["report"] == "get_surcharge":
                            return {
                                "employee_uuid": EmployeesInput,
                            }
                    else:
                        return {"report": ReportSurchargeInput}

            else:
                return {
                    "reports_salary-setting": ReportsSalarySettingInput,
                }
        # Запрос ЗП по груп. акс. по одлноту сотруднику за период
        if session.params["inputs"]["0"]["reports"] == "get_salary_aks":
            return {
                "employee_uuid": EmployeesInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePastInput,
                "closeDate": CloseDatePastInput,
            }
        # Запрос ЗП за выполнение. плана по одлноту сотруднику за период
        if session.params["inputs"]["0"]["reports"] == "get_salary_plan_day":
            return {
                "employee_uuid": EmployeesInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePastInput,
                "closeDate": CloseDatePastInput,
            }
        # Запрос ЗП за выполнение. плана по одлноту сотруднику за период
        if session.params["inputs"]["0"]["reports"] == "get_salary_day":
            return {
                "employee_uuid": EmployeesInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePastInput,
                "closeDate": CloseDatePastInput,
            }

        if session.params["inputs"]["0"]["reports"] == "get_salary_motivation_uuid":
            return {
                "employee_uuid": EmployeesInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePastInput,
                "closeDate": CloseDatePastInput,
            }

        # ЗП ИТОГО
        if session.params["inputs"]["0"]["reports"] == "get_salary_total":
            if "period" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["period"] == "day":
                    return {}
                if session.params["inputs"]["0"]["period"] not in period:
                    return {"openDate": OpenDatePastInput}
                else:
                    return {
                        "openDate": OpenDatePastInput,
                        "closeDate": CloseDatePastInput,
                    }
            else:
                return {
                    "employee_uuid": EmployeesInput,
                    "period": PeriodDateInput,
                }
        #
        if session.params["inputs"]["0"]["reports"] == "get_salary_total_day":
            if "period" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["period"] == "day":
                    return {}
                if session.params["inputs"]["0"]["period"] not in period:
                    return {"openDate": OpenDatePastInput}
                else:
                    return {
                        "openDate": OpenDatePastInput,
                        # "closeDate": CloseDatePastInput,
                    }
            else:
                return {
                    "period": PeriodDateInput,
                }

    else:
        return {"reports": ReportSalaryInput}


def generate(session: Session):
    pprint(session.params["inputs"]["0"])
    params = session.params["inputs"]["0"]
    user_id = session.user_id
    room = session["room"]

    # Назначить группы аксессуаров
    if "report" in params:
        if params["report"] == "assigning_group_uuid_accessory":
            # Получение идентификаторов магазинов пользователя
            shops_id = get_shops_uuid_user_id(session)
            # Список для хранения родительских UUID
            parentUuids = []

            # содоет ключи в session.params["inputs"]
            for i in range(int(room) + 1):
                # Проверяем, есть ли "parentUuid" в параметрах комнаты i
                if "parentUuid" in session.params["inputs"][str(i)]:
                    # Добавляем "parentUuid" в список
                    parentUuids.append(session.params["inputs"][str(i)]["parentUuid"])

            # Получаем текущую дату и время в формате ISO
            close_date = utcnow().isoformat()[:10]

            # Итерируемся по идентификаторам магазинов
            for shop_id in shops_id:
                # Создаем словарь с данными для обновления в базе данных
                dict_ = {
                    "shop_id": shop_id,
                    "closeDate": close_date,
                    "parentUuids": parentUuids,
                    "user_id": user_id,
                    "x_type": "MOTIVATION_PARENT_UUID",
                }

                # Обновляем или добавляем запись в базе данных
                GroupUuidAks.objects(
                    shop_id=shop_id,
                    closeDate=close_date,
                    x_type="MOTIVATION_PARENT_UUID",
                ).update(**dict_, upsert=True)

            # Получаем названия магазинов по их идентификаторам
            shops = Shop.objects(uuid__in=shops_id).only("name")

            shop_name = ""

            # Собираем названия магазинов в строку
            for shop in shops:
                shop_name += "{}, ".format(shop.name)

            # Формируем результат в виде списка словарей
            result = [
                {"ДАТА:": close_date},
                {"ГРУППЫ:": "ЗП АКС"},
                {"МАГАЗИН(Ы):".upper(): shop_name},
            ]

            number_ = 1

            # Нумеруем и добавляем информацию о продуктах для каждого родительского UUID
            for uuid in parentUuids:
                products = Products.objects(group=True, uuid=uuid).first()
                result.append({"{}:".format(number_): products.name})
                number_ += 1

            # Возвращаем результат
            return result
        # Запрос назначенных групп аксессуаров
        if params["report"] == "get_group_uuid_accessory":
            # Получаем информацию о магазинах
            shops = get_shops(session)
            shop_id_ = shops["shop_id"]
            shop_name = shops["shop_name"]

            # Получаем последние документы по групповым UUID с типом "MOTIVATION_PARENT_UUID"
            documents = (
                GroupUuidAks.objects(
                    shop_id=shop_id_[0], x_type="MOTIVATION_PARENT_UUID"
                )
                .order_by("-closeDate")
                .first()
            )

            # Получаем продукты, относящиеся к parentUuid
            products = Products.objects(group=True, uuid__in=documents.parentUuids)

            result = [{"МАГАЗИН": shop_name}]
            number_ = 1
            uuid = []
            for prod in products:
                if prod["uuid"] not in uuid:
                    result.append({"{}".format(number_): prod["name"]})
                    uuid.append(prod["uuid"])
                    number_ += 1
            return result

        # Назначить товар доб. мотивации
        if params["report"] == "product_ext_motivation":
            # Получаем UUID магазинов
            shops_id = get_shops_uuid_user_id(session)

            motivationUuids = {}

            # Создаем словарь с мотивацией для каждого UUID из параметров
            for i in range(int(room) + 1):
                # если в 'uuid' есть в session.params["inputs"][str(i)]
                if "uuid" in session.params["inputs"][str(i)]:
                    # если 'uuid' нет в словаре с ключем i в списке uuid
                    motivationUuids.update(
                        {
                            session.params["inputs"][str(i)]["uuid"]: int(
                                session.params["inputs"][str(i)]["motivation"]
                            )
                        }
                    )
            print(motivationUuids)

            # Устанавливаем текущую дату в формате ISO
            close_date = utcnow().isoformat()[:10]

            # Обновляем или создаем документы GroupUuidAks для каждого магазина
            for shop_id in shops_id:
                dict_ = {
                    "closeDate": close_date,
                    "uuid": motivationUuids,
                    "user_id": user_id,
                    "x_type": "MOTIVATION_UUID",
                }

                GroupUuidAks.objects(
                    shop_id=shop_id, closeDate=close_date, x_type="MOTIVATION_UUID"
                ).update(**dict_, upsert=True)

            # Получаем имена магазинов
            shops = Shop.objects(uuid__in=shops_id).only("name")
            shop_name = ""
            for shop in shops:
                shop_name += "{}, ".format(shop.name)

            result = [
                {"Товар доб. мотивации".upper(): ""},
                {"МАГАЗИН(Ы):".upper(): shop_name},
            ]

            # Формируем результат в виде списка словарей с информацией о товарах и мотивации
            for uuid, motivation in motivationUuids.items():
                products = Products.objects(group=False, uuid=uuid).first()
                result.append({"{}:".format(products.name): "{}₱".format(motivation)})

                # pprint(item)
            return result
        # Запрос назначенных товаров доб. мотивации
        if params["report"] == "get_product_ext_motivation":
            # Получение информации о магазине
            shops = get_shops(session)
            shop_id_ = shops["shop_id"]
            shop_name = shops["shop_name"]

            # Получение документов с типом "MOTIVATION_UUID" для последней закрывшейся даты
            documents = (
                GroupUuidAks.objects(shop_id=shop_id_[0], x_type="MOTIVATION_UUID")
                .order_by("-closeDate")
                .first()
            )

            # Получение продуктов на основе UUID из документов
            products = Products.objects(group=False, uuid__in=documents.uuid)

            result = [{"Товар доб. мотивации".upper(): ""}, {"МАГАЗИН": shop_name}]

            # Формирование результата с информацией о каждом товаре и его мотивации
            for uuid, motivation in documents.uuid.items():
                products = Products.objects(group=False, uuid=uuid).first()
                result.append({"{}:".format(products.name): "{}₱".format(motivation)})

            return result

        # Назначить оклады на ТТ
        if params["report"] == "assigning_salary_":
            # Получение текущей даты
            close_date = utcnow().isoformat()[:10]
            shop_result = {}
            # содоет ключи в session.params["inputs"]
            for i in range(int(room) + 1):
                # если в 'uuid' есть в session.params["inputs"][str(i)]

                _dict = {
                    "closeDate": close_date,
                    "salary": int(session.params["inputs"][str(i)]["salary"]),
                    "user_id": user_id,
                    "shop_id": session.params["inputs"][str(i)]["shop"],
                    "x_type": "SALARY",
                }
                pprint(_dict)

                shop_result.update(
                    {session.params["inputs"][str(i)]["shop"]: _dict["salary"]}
                )

                GroupUuidAks.objects(
                    shop_id=_dict["shop_id"], closeDate=close_date, x_type="SALARY"
                ).update(**_dict, upsert=True)

            result = []

            for k, v in shop_result.items():
                shop = Shop.objects(uuid=k).only("name").first()
                result.append({shop.name: "{}₱".format(v)})

            return result
        # Запрос назначенных окладов
        if params["report"] == "get_salary":
            # Получение информации о магазине
            shops = get_shops(session)
            shop_id_ = shops["shop_id"]
            shop_name = shops["shop_name"]

            documents = (
                GroupUuidAks.objects(shop_id=shop_id_[0], x_type="SALARY")
                .order_by("-closeDate")
                .first()
            )

            result = [
                {"ДАТА:": documents.closeDate},
                {"ОКЛАД:": "{}₱".format(documents.salary)},
                {"МАГАЗИН(Ы):": shop_name},
            ]
            return result
        # Назначить сум. за выпол. пл.
        if params["report"] == "amount_of_motivation":
            # Получение текущей даты
            close_date = utcnow().isoformat()[:10]
            _dict = {"motivation": int(params["motivation"])}

            shop_result = {}
            # содоет ключи в session.params["inputs"]
            for i in range(int(room) + 1):
                # если в 'uuid' есть в session.params["inputs"][str(i)]
                _dict = {
                    "closeDate": close_date,
                    "motivation": int(session.params["inputs"][str(i)]["motivation"]),
                    "user_id": user_id,
                    "shop_id": session.params["inputs"][str(i)]["shop"],
                    "x_type": "MOTIVATION",
                }

                shop_result.update(
                    {session.params["inputs"][str(i)]["shop"]: _dict["motivation"]}
                )

                GroupUuidAks.objects(
                    shop_id=_dict["shop_id"], closeDate=close_date, x_type="MOTIVATION"
                ).update(**_dict, upsert=True)

            result = []
            for k, v in shop_result.items():
                shop = Shop.objects(uuid=k).only("name").first()
                pprint(shop.name)
                result.append({shop.name: "{}₱".format(v)})

            return result
        # Запрос назначенной мотвации за выполнение плана
        if params["report"] == "get_amount_of_motivation":
            shops = get_shops(session)
            shop_id_ = shops["shop_id"]
            shop_name = shops["shop_name"]
            documents = (
                GroupUuidAks.objects(shop_id=shop_id_[0], x_type="MOTIVATION")
                .order_by("-closeDate")
                .first()
            )
            if documents:
                return [
                    {"ДАТА:": documents.closeDate},
                    {"СУММА МОТИВАЦИ:": "{}₱".format(documents.motivation)},
                    {"МАГАЗИН(Ы):": shop_name},
                ]
            else:
                return [{"Нет данных".upper(): ""}]
        # Назначить доплату к зп
        if params["report"] == "assign_a_surcharge":
            close_date = utcnow().isoformat()[:10]
            employee_result = {}
            for i in range(int(room) + 1):
                _dict = {
                    "closeDate": close_date,
                    "employee_uuid": session.params["inputs"][str(i)]["uuid"],
                    "user_id": user_id,
                    "surcharge": int(session.params["inputs"][str(i)]["surcharge"]),
                    "x_type": "ASSING_A_SURCHARGE",
                }
                employee_result.update(
                    {
                        session.params["inputs"][str(i)]["uuid"]: session.params[
                            "inputs"
                        ][str(i)]["surcharge"]
                    }
                )
                GroupUuidAks.objects(
                    employee_uuid=session.params["inputs"][str(i)]["uuid"],
                    closeDate=close_date,
                    x_type="ASSING_A_SURCHARGE",
                ).update(**_dict, upsert=True)

            result = []
            for k, v in employee_result.items():
                employee = Employees.objects(lastName=k).only("name").first()
                result.append({"{}:".format(employee.name): "{}₱".format(v)})

            return result
        # Запрос назначенной сум. доплат к зп
        if params["report"] == "get_surcharge":
            employee_uuid = params["employee_uuid"]
            employee = Employees.objects(lastName=employee_uuid).only("name").first()
            documents = (
                GroupUuidAks.objects(
                    employee_uuid=employee_uuid, x_type="ASSING_A_SURCHARGE"
                )
                .order_by("-closeDate")
                .first()
            )

            if documents:
                return [
                    {"ДАТА:": documents.closeDate},
                    {"СУММА ДОПЛАТЫ:": "{}₱".format(documents.surcharge)},
                    {"СОТРУДНИК:": employee.name},
                ]
            else:
                return [{"Нет данных".upper(): ""}]
    else:
        # Запрос ЗП по груп. акс. по одлноту сотруднику за период
        if params["reports"] == "get_salary_aks":
            result = []

            # Получение фамилии сотрудника из параметров
            employee_last_name = params["employee_uuid"]

            # Получение списка uuid сотрудников с заданной фамилией из базы данных
            user = [
                element.uuid
                for element in Employees.objects(lastName=employee_last_name)
            ]
            pprint(user)

            # Получение периода из сессии
            period = get_period(session)
            since = period["since"]
            until = period["until"]

            # Разбивка периода на интервалы дней
            intervals = get_intervals(since, until, "days", 1)

            # Итерация по интервалам
            for since_, until_ in intervals:
                documents_open_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since_, "$lt": until_},
                        "openUserUuid": {"$in": user},
                        "x_type": "OPEN_SESSION",
                    }
                ).first()

                # Проверка наличия открытой сессии
                if documents_open_session:
                    shop = (
                        Shop.objects(uuid=documents_open_session.shop_id)
                        .only("name")
                        .first()
                    )

                    documents_aks = (
                        GroupUuidAks.objects(
                            __raw__={
                                "closeDate": {"$lte": until_[:10]},
                                "shop_id": documents_open_session.shop_id,
                                "x_type": "MOTIVATION_PARENT_UUID",
                            }
                        )
                        .order_by("-closeDate")
                        .first()
                    )

                    group = Products.objects(
                        __raw__={
                            "shop_id": documents_open_session.shop_id,
                            # 'group': True,
                            "parentUuid": {"$in": documents_aks.parentUuids},
                        }
                    )

                    products_uuid = [i.uuid for i in group]

                    documents_sale = Documents.objects(
                        __raw__={
                            "closeDate": {"$gte": since, "$lt": until},
                            "shop_id": documents_open_session.shop_id,
                            "x_type": "SELL",
                            "transactions.commodityUuid": {"$in": products_uuid},
                        }
                    )
                    _dict = {}
                    sum_sales = 0
                    for doc in documents_sale:
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "REGISTER_POSITION":
                                if trans["commodityUuid"] in products_uuid:
                                    if trans["commodityName"] in _dict:
                                        _dict[trans["commodityName"]] += trans["sum"]
                                        sum_sales += trans["sum"]
                                    else:
                                        _dict[trans["commodityName"]] = trans["sum"]
                                        sum_sales += trans["sum"]
                    _dict = dict(
                        OrderedDict(sorted(_dict.items(), key=lambda t: -t[1]))
                    )
                    _dict_total = {}
                    for k, v in _dict.items():
                        _dict_total[k] = "{}₽".format(v)

                    _dict_total.update(
                        {
                            "СУММА:": "{}₽".format(sum_sales),
                            "ПРОЦЕНТ:": "5%",
                            "ЗП": "{}₽".format(
                                round(int(sum_sales / 100 * 5) / 10) * 10
                            ),
                            "ДАТА:": since[:10],
                            "МАГАЗИН": shop.name,
                        }
                    )
                    result.append(_dict_total)

            return result
        # Запрос ЗП за мотив. товар по одлноту сотруднику за период
        if params["reports"] == "get_salary_motivation_uuid":
            result = []
            employee_last_name = params["employee_uuid"]
            user = [
                element.uuid
                for element in Employees.objects(lastName=employee_last_name)
            ]
            pprint(user)

            period = get_period(session)
            since = period["since"]
            until = period["until"]

            intervals = get_intervals(since, until, "days", 1)
            for since_, until_ in intervals:
                documents_open_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since_, "$lt": until_},
                        "openUserUuid": {"$in": user},
                        "x_type": "OPEN_SESSION",
                    }
                ).first()
                if documents_open_session:
                    shop = (
                        Shop.objects(uuid=documents_open_session.shop_id)
                        .only("name")
                        .first()
                    )

                    documents_mot = (
                        GroupUuidAks.objects(
                            __raw__={
                                "closeDate": {"$lte": until_[:10]},
                                "shop_id": documents_open_session.shop_id,
                                "x_type": "MOTIVATION_UUID",
                            }
                        )
                        .order_by("-closeDate")
                        .first()
                    )
                    if documents_mot:
                        products_uuid = [k for k, v in documents_mot.uuid.items()]

                        documents_sale = Documents.objects(
                            __raw__={
                                "closeDate": {"$gte": since_, "$lt": until_},
                                "shop_id": documents_open_session.shop_id,
                                "x_type": "SELL",
                                "transactions.commodityUuid": {"$in": products_uuid},
                            }
                        )
                        dict_salary = {}
                        sum_mot = 0
                        for doc in documents_sale:
                            for trans in doc["transactions"]:
                                if trans["x_type"] == "REGISTER_POSITION":
                                    if trans["commodityUuid"] in products_uuid:
                                        if trans["commodityUuid"] in dict_salary:
                                            dict_salary[
                                                trans["commodityUuid"]
                                            ] += trans["quantity"]

                                        else:
                                            dict_salary[trans["commodityUuid"]] = trans[
                                                "quantity"
                                            ]

                                        pprint(dict_salary)

                        dict_salary = dict(
                            OrderedDict(
                                sorted(dict_salary.items(), key=lambda t: -t[1])
                            )
                        )
                        _dict_total = {}
                        for k, v in dict_salary.items():
                            prod_name = Products.objects(uuid=k).only("name").first()
                            _dict_total[prod_name.name] = "{}₽".format(
                                v * documents_mot.uuid[k]
                            )

                        _dict_total.update(
                            {
                                "СУММА ЗП:": "{}₽".format(
                                    round(int(sum_mot / 100 * 5) / 10) * 10
                                ),
                                "ДАТА:": since_[:10],
                                "МАГАЗИН": shop.name,
                            }
                        )
                        result.append(_dict_total)
                    else:
                        result.append({since_[:10]: "Нет данных".upper()})
            return result
        #  # ЗП ИТОГО
        if params["reports"] == "get_salary_total":
            # 'bonus за вып. плана'.upper(): '{}₱'.format(),
            # 'percent за аксс'.upper(): '{}%'.format(),
            # 'Оклад'.upper(): '{}₱'.format(),
            # 'Доплата'.upper(): '{}₱'.format(),
            # 'План'.upper(): '{}₱'.format(),
            # 'Продажи'.upper(): '{}₱'.format(),
            # 'Продавец'.upper(): '',
            # 'Магазин'.upper(): '',
            # 'Дата'.upper(): '',
            # 'Итго зарплата'.upper(): '{}₱'.format(),
            result = []
            employee_last_name = params["employee_uuid"]
            user = [
                element.uuid
                for element in Employees.objects(lastName=employee_last_name)
            ]
            # pprint(user)
            period = get_period(session)
            since = period["since"]
            until = period["until"]

            intervals = get_intervals(since, until, "days", 1)
            for since_, until_ in intervals:
                # pprint(since_)
                # pprint(until_)
                documents_open_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since_, "$lt": until_},
                        "openUserUuid": {"$in": user},
                        "x_type": "OPEN_SESSION",
                    }
                ).first()
                pprint(documents_open_session)
                if documents_open_session:
                    # Название магазина (shop.name)
                    shop = (
                        Shop.objects(uuid=documents_open_session.shop_id)
                        .only("name")
                        .first()
                    )
                    sho_id = documents_open_session.shop_id
                    employee_uuid = documents_open_session.openUserUuid
                    employee = (
                        Employees.objects(uuid=employee_uuid).only("name").first()
                    )
                    total_salary = get_total_salary(
                        employee_last_name, sho_id, since_, until_
                    )
                    result.append(
                        {
                            "Продажа аксс:".upper(): "{}₱".format(
                                total_salary["accessory_sum_sell"]
                            ),
                            "bonus за аксс:".upper(): "{}₱".format(
                                total_salary["bonus_accessory"]
                            ),
                            "bonus за мотиа. тов.:".upper(): "{}₱".format(
                                total_salary["bonus_motivation"]
                            ),
                            "План по Электронкам:".upper(): "{}₱".format(
                                total_salary["plan_motivation_prod"]
                            ),
                            "Продажи по Электронкам:".upper(): "{}₱".format(
                                total_salary["sales_motivation_prod"]
                            ),
                            "bonus за вып. плана:".upper(): "{}₱".format(
                                total_salary["bonus_motivation_prod"]
                            ),
                            "percent за аксс:".upper(): "{}%".format(5),
                            "Оклад:".upper(): "{}₱".format(total_salary["salary"]),
                            "Доплата:".upper(): "{}₱".format(total_salary["surcharge"]),
                            "Продавец:".upper(): employee.name.upper(),
                            "Магазин:".upper(): shop.name.upper(),
                            "Дата:".upper(): until_[:10],
                            "Итго зарплата".upper(): "{}₱".format(
                                total_salary["total_salary"]
                            ),
                        }
                    )
                    # result.append(
                    #     get_total_salary(employee_last_name, sho_id, since_, until_)
                    # )
                    # result.append(get_mot_salary(sho_id, since_, until_))
                    # result.append(get_plan_bonus(sho_id, since_, until_))
                    # result.append(get_salary(sho_id, until_))
                    # result.append(get_surcharge(employee_last_name, until_))

                else:
                    result.append({until_[:10]: "ВЫХОДНОЙ"})
            return result
        #
        if params["reports"] == "get_salary_total_day":
            result = []

            period = get_period_day(session)
            since = period["since"]
            until = period["until"]

            intervals = get_intervals(since, until, "days", 1)
            for since_, until_ in intervals:
                documents_open_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since_, "$lt": until_},
                        # "openUserUuid": {"$in": user},
                        "x_type": "OPEN_SESSION",
                    }
                )
                # pprint(documents_open_session)
                for doc in documents_open_session:
                    # Название магазина (shop.name)
                    shop = Shop.objects(uuid=doc["shop_id"]).only("name").first()
                    sho_id = doc["shop_id"]
                    employee_uuid = doc["openUserUuid"]
                    employee = Employees.objects(uuid=employee_uuid).first()
                    total_salary = get_total_salary(
                        employee.lastName, sho_id, since_, until_
                    )
                    result.append(
                        {
                            "Продажа аксс:".upper(): "{}₱".format(
                                total_salary["accessory_sum_sell"]
                            ),
                            "bonus за аксс:".upper(): "{}₱".format(
                                total_salary["bonus_accessory"]
                            ),
                            "bonus за мотиа. тов.:".upper(): "{}₱".format(
                                total_salary["bonus_motivation"]
                            ),
                            "План по Электронкам:".upper(): "{}₱".format(
                                total_salary["plan_motivation_prod"]
                            ),
                            "Продажи по Электронкам:".upper(): "{}₱".format(
                                total_salary["sales_motivation_prod"]
                            ),
                            "bonus за вып. плана:".upper(): "{}₱".format(
                                total_salary["bonus_motivation_prod"]
                            ),
                            "percent за аксс:".upper(): "{}%".format(5),
                            "Оклад:".upper(): "{}₱".format(total_salary["salary"]),
                            "Доплата:".upper(): "{}₱".format(total_salary["surcharge"]),
                            "Продавец:".upper(): employee.name.upper(),
                            "Магазин:".upper(): shop.name.upper(),
                            "Дата:".upper(): until_[:10],
                            "Итго зарплата".upper(): "{}₱".format(
                                total_salary["total_salary"]
                            ),
                        }
                    )

            return result
        # Запрос ЗП за выполнение. плана по одлноту сотруднику за период
        if params["reports"] == "get_salary_plan_day":
            group_id = (
                "78ddfd78-dc52-11e8-b970-ccb0da458b5a",
                "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
                "0627db0b-4e39-11ec-ab27-2cf05d04be1d",
                "2b8eb6b4-92ea-11ee-ab93-2cf05d04be1d",
                "8a8fcb5f-9582-11ee-ab93-2cf05d04be1d",
                "97d6fa81-84b1-11ea-b9bb-70c94e4ebe6a",
                "ad8afa41-737d-11ea-b9b9-70c94e4ebe6a",
                "568905bd-9460-11ee-9ef4-be8fe126e7b9",
                "568905be-9460-11ee-9ef4-be8fe126e7b9",
            )
            # Инициализация пустого списка для хранения результатов
            result = []
            # Получение фамилии сотрудника из параметра
            employee_last_name = params["employee_uuid"]
            # Извлекаем UUID сотрудника из базы данных по фамилии
            user_uuid = [
                element.uuid
                for element in Employees.objects(lastName=employee_last_name)
            ]

            user = Employees.objects(lastName=employee_last_name).only("name").first()

            # Получение периода из сессии
            period = get_period(session)

            # Получение начальной и конечной дат периода
            since = period["since"]
            until = period["until"]

            # Получение интервалов между датами с шагом в 1 день
            intervals = get_intervals(since, until, "days", 1)
            total_salary_plan = 0
            # Итерируем по интервалам
            for since_, until_ in intervals:
                # Поиск документов типа "OPEN_SESSION" за указанный период
                documents_open_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since_, "$lt": until_},
                        "openUserUuid": {"$in": user_uuid},
                        "x_type": "OPEN_SESSION",
                    }
                ).first()
                # Если найдена открытая сессия документов
                if documents_open_session:
                    # Получаем магазин, связанный с этим документом
                    shop = (
                        Shop.objects(uuid=documents_open_session.shop_id)
                        .only("name")
                        .first()
                    )

                    # Получение данных о планах продаж для магазина
                    documents_plan = (
                        Plan.objects(
                            __raw__={
                                "closeDate": {"$gte": since_, "$lt": until_},
                                "shop_id": documents_open_session.shop_id,
                            }
                        )
                        .order_by("-closeDate")
                        .first()
                    )

                    # pprint(documents_plan)
                    data_plan = {}
                    sum_plan = 0
                    if documents_plan:
                        sum_plan = documents_plan.sum
                    else:
                        sum_plan = "no data"

                    # Получение списка продуктов, относящихся к группам товаров
                    products = Products.objects(
                        __raw__={
                            "shop_id": documents_open_session.shop_id,
                            "parentUuid": {"$in": group_id},
                        }
                    )

                    # Формирование списка идентификаторов продуктов
                    products_uuid = [element.uuid for element in products]

                    # Типы операций для анализа (продажи и возвраты)
                    x_type = ["SELL", "PAYBACK"]

                    # Получение документов о продажах и возвратах для продуктов
                    documents_2 = Documents.objects(
                        __raw__={
                            "closeDate": {"$gte": since_, "$lt": until_},
                            "shop_id": documents_open_session.shop_id,
                            "x_type": {"$in": x_type},
                            "transactions.commodityUuid": {"$in": products_uuid},
                        }
                    )
                    sum_sell_today = 0

                    # Вычисление суммы продаж за текущий период
                    for doc_2 in documents_2:
                        for trans_2 in doc_2["transactions"]:
                            if trans_2["x_type"] == "REGISTER_POSITION":
                                if trans_2["commodityUuid"] in products_uuid:
                                    sum_sell_today += trans_2["sum"]

                    # data_plan.update({"Прод": sum_sell_today})

                    documents_plan_motivation = (
                        GroupUuidAks.objects(
                            __raw__={
                                "closeDate": {"$lte": until_[:10]},
                                "shop_id": documents_open_session.shop_id,
                                "x_type": "MOTIVATION",
                            }
                        )
                        .order_by("-closeDate")
                        .first()
                    )

                    # Если есть документы по плану мотивации
                    if documents_plan_motivation:
                        # Если данные по плану равны "no data"
                        if sum_plan == "no data":
                            symbol = "🔴"
                            salary_plan = "no data"
                        else:
                            # Если сумма продаж сегодня больше или равна установленному плану
                            if sum_sell_today >= sum_plan:
                                symbol = "✅"
                                salary_plan = documents_plan_motivation["motivation"]
                                total_salary_plan += documents_plan_motivation[
                                    "motivation"
                                ]
                            else:
                                symbol = "🟡"
                                salary_plan = 0
                    else:
                        symbol = "🔴"
                        salary_plan = 0

                    # Обновление данных плана
                    data_plan.update(
                        {
                            "План:".upper(): f"{sum_plan}₱",
                            "Прод:".upper(): f"{sum_sell_today}₱",
                            "Зп:".upper(): f"{salary_plan}₱",
                            "Магазин:".upper(): shop.name,
                        }
                    )
                    data_plan.update(
                        {
                            symbol: " ",
                        }
                    )
                    pprint(data_plan)
                    result.append(data_plan)
            result.append(
                {
                    "Начало периода:".upper(): since[0:10],
                    "Окончание периода:".upper(): until[0:10],
                    "Продавец:".upper(): user.name,
                    "Итого зп:".upper(): f"{total_salary_plan}₱",
                }
            )
            return result
        if params["reports"] == "get_salary_day":

            def process_interval(interval, user: str):
                """
                Обработка данных для указанного временного интервала.

                Args:
                    interval (tuple): Кортеж, представляющий временной интервал (since, until).
                    user (list): Список UUID сотрудников.

                Returns:
                    list: Список результатов обработки интервала.
                """
                since, until = interval

                # Получение документов для открытой сессии в указанный интервал времени
                documents_open_session = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "openUserUuid": {"$in": user},
                        "x_type": "OPEN_SESSION",
                    }
                ).first()

                result = []

                if documents_open_session:
                    # Если есть открытая сессия, получаем информацию о магазине
                    shop = (
                        Shop.objects(uuid=documents_open_session.shop_id)
                        .only("name")
                        .first()
                    )

                    # Получение группы по идентификатору магазина
                    documents_aks = (
                        GroupUuidAks.objects(
                            __raw__={
                                "closeDate": {"$lte": until[:10]},
                                "shop_id": documents_open_session.shop_id,
                                "x_type": "MOTIVATION_PARENT_UUID",
                            }
                        )
                        .order_by("-closeDate")
                        .first()
                    )

                    if documents_aks:
                        group = Products.objects(
                            __raw__={
                                "shop_id": documents_open_session.shop_id,
                                "parentUuid": {"$in": documents_aks.parentUuids},
                            }
                        )

                        products_uuid = [i.uuid for i in group]

                        # Получение документов о продажах в указанный интервал времени
                        documents_sale = Documents.objects(
                            __raw__={
                                "closeDate": {"$gte": since, "$lt": until},
                                "shop_id": documents_open_session.shop_id,
                                "x_type": "SELL",
                                "transactions.commodityUuid": {"$in": products_uuid},
                            }
                        )

                        sum_sales = sum(
                            decimal.Decimal(trans["sum"])
                            for doc in documents_sale
                            for trans in doc["transactions"]
                            if trans["x_type"] == "REGISTER_POSITION"
                            and trans["commodityUuid"] in products_uuid
                        )

                        # Вычисление зарплаты за день
                        salary_total_day = decimal.Decimal(sum_sales) / 100 * 5

                        result.append(
                            {
                                "СУММА:": f"{sum_sales}₽",
                                "ПРОЦЕНТ:": "5%",
                                "ЗП": f"{salary_total_day}₽",
                                "ДАТА:": documents_open_session.closeDate[:10],
                                "МАГАЗИН": shop.name,
                            }
                        )

                else:
                    # Если нет открытой сессии - выходной день
                    result.append(
                        {
                            "🏖️ выходной день:".upper(): since[:10],
                        }
                    )

                return result

            def get_salary_aks_p(session):
                """
                Получение данных о продажах и зарплате для каждого временного интервала.

                Args:
                    session: Объект сессии.

                Returns:
                    tuple: Список результатов обработки интервалов, общая сумма продаж и общая зарплата.
                """
                result = []

                employee_last_name = params["employee_uuid"]

                employee_name = (
                    Employees.objects(lastName=employee_last_name).only("name").first()
                )

                user = [
                    element.uuid
                    for element in Employees.objects(lastName=employee_last_name)
                ]

                since = (
                    get(session.params["inputs"]["0"]["openDate"])
                    .replace(hour=23, minute=0)
                    .isoformat()
                )
                until = (
                    get(session.params["inputs"]["0"]["closeDate"])
                    .replace(hour=23, minute=0)
                    .isoformat()
                )

                intervals = get_intervals(since, until, "days", 1)

                # Параллельное выполнение задач
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    tasks = [
                        executor.submit(process_interval, interval, user)
                        for interval in intervals
                    ]

                    for task in concurrent.futures.as_completed(tasks):
                        result.extend(task.result())

                # Вычисление общей суммы продаж и общей зарплаты
                data_total_sall = sum(
                    decimal.Decimal(item["СУММА:"][:-1])
                    for item in result
                    if "СУММА:" in item
                )
                data_total_salary = sum(
                    decimal.Decimal(item["ЗП"][:-1]) for item in result if "ЗП" in item
                )

                result.append(
                    {
                        "⬇️⬇️⬇️⬇️⬇️Итого⬇️⬇️⬇️⬇️⬇️".upper(): " ",
                        "ПРОДАЖИ:": f"{data_total_sall}₽",
                        "ПРОЦЕНТ:": "5%",
                        "ЗП": f"{data_total_salary}₽",
                        "Начало периода:": since[0:10],
                        "Окончание периода:": until[0:10],
                        "Продавец:".upper(): employee_name.name.upper(),
                    }
                )

                return result

            result = get_salary_aks_p(session)

            return result

            # result = []

            # # Получение фамилии сотрудника из параметров
            # employee_last_name = params["employee_uuid"]
            # employee_name = (
            #     Employees.objects(lastName=employee_last_name).only("name").first()
            # )

            # # Получение списка uuid сотрудников с заданной фамилией из базы данных
            # user = [
            #     element.uuid
            #     for element in Employees.objects(lastName=employee_last_name)
            # ]

            # # Получение периода из сессии
            # since = (
            #     get(session.params["inputs"]["0"]["openDate"])
            #     .replace(hour=23, minute=00)
            #     .isoformat()
            # )
            # until = (
            #     get(session.params["inputs"]["0"]["closeDate"])
            #     .replace(hour=23, minute=00)
            #     .isoformat()
            # )

            # # Разбивка периода на интервалы дней
            # intervals = get_intervals(since, until, "days", 1)

            # data_total_sall = 0
            # data_total_salary = 0

            # # Итерация по интервалам
            # for since_, until_ in intervals:
            #     # pprint(since_)
            #     documents_open_session = Documents.objects(
            #         __raw__={
            #             "closeDate": {"$gte": since_, "$lt": until_},
            #             "openUserUuid": {"$in": user},
            #             "x_type": "OPEN_SESSION",
            #         }
            #     ).first()

            #     # Проверка наличия открытой сессии
            #     if documents_open_session:
            #         shop = (
            #             Shop.objects(uuid=documents_open_session.shop_id)
            #             .only("name")
            #             .first()
            #         )

            #         # Получение группы по идентификатору магазина
            #         documents_aks = (
            #             GroupUuidAks.objects(
            #                 __raw__={
            #                     "closeDate": {"$lte": until_[:10]},
            #                     "shop_id": documents_open_session.shop_id,
            #                     "x_type": "MOTIVATION_PARENT_UUID",
            #                 }
            #             )
            #             .order_by("-closeDate")
            #             .first()
            #         )

            #         if documents_aks:
            #             group = Products.objects(
            #                 __raw__={
            #                     "shop_id": documents_open_session.shop_id,
            #                     # 'group': True,
            #                     "parentUuid": {"$in": documents_aks.parentUuids},
            #                 }
            #             )

            #             products_uuid = [i.uuid for i in group]

            #             documents_sale = Documents.objects(
            #                 __raw__={
            #                     "closeDate": {"$gte": since_, "$lt": until_},
            #                     "shop_id": documents_open_session.shop_id,
            #                     "x_type": "SELL",
            #                     "transactions.commodityUuid": {"$in": products_uuid},
            #                 }
            #             )

            #             sum_sales = 0

            #             for doc in documents_sale:
            #                 for trans in doc["transactions"]:
            #                     if trans["x_type"] == "REGISTER_POSITION":
            #                         if trans["commodityUuid"] in products_uuid:
            #                             sum_sales += decimal.Decimal(trans["sum"])
            #             salary_total_day = (
            #                 decimal.Decimal(sum_sales)
            #                 / decimal.Decimal(100)
            #                 * decimal.Decimal(5)
            #             )

            #             data_total_sall += decimal.Decimal(sum_sales)
            #             data_total_salary += decimal.Decimal(salary_total_day)

            #             result.append(
            #                 {
            #                     "СУММА:": f"{sum_sales}₽",
            #                     "ПРОЦЕНТ:": "5%",
            #                     "ЗП": f"{salary_total_day}₽",
            #                     "ДАТА:": documents_open_session.closeDate[:10],
            #                     "МАГАЗИН": shop.name,
            #                 }
            #             )

            #     else:
            #         pprint("no data")
            #         result.append(
            #             {
            #                 "🏖️ выходной день:".upper(): since_[:10],
            #             }
            #         )

            # result.append(
            #     {
            #         "⬇️⬇️⬇️⬇️⬇️Итого⬇️⬇️⬇️⬇️⬇️".upper(): " ",
            #         "ПРОДАЖИ:": f"{data_total_sall}₽",
            #         "ПРОЦЕНТ:": "5%",
            #         "ЗП": f"{data_total_salary}₽",
            #         "Начало периода:": since[0:10],
            #         "Окончание периода:": until[0:10],
            #         "Продавец:".upper(): employee_name.name.upper(),
            #         "МАГАЗИН": shop.name,
            #     }
            # )

            # return result
