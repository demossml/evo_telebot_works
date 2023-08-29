from bd.model import Shop, Products, Documents, Session, Employees, GroupUuidAks
from .util import (
    get_shops_uuid_user_id,
    get_period,
    get_aks_salary,
    get_shops,
    get_intervals,
    get_mot_salary,
    get_plan_bonus,
    get_salary,
    get_surcharge,
    get_total_salary,
)
from pprint import pprint
from collections import OrderedDict
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


name = "🛒 Зарплата ➡️".upper()
desc = ""
mime = "text"


class MotivationInput:
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
    period = ["day", "week", "fortnight", "month"]
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
                            return {"motivation": MotivationInput}
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
        # Запрос ЗП за мотив. товар по одлноту сотруднику за период
        if session.params["inputs"]["0"]["reports"] == "get_salary_motivation_uuid":
            return {
                "employee_uuid": EmployeesInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePastInput,
                "closeDate": CloseDatePastInput,
            }
        # ЗП ИТОГО
        if session.params["inputs"]["0"]["reports"] == "get_salary_total":
            return {
                "employee_uuid": EmployeesInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePastInput,
                "closeDate": CloseDatePastInput,
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
            shops_id = get_shops_uuid_user_id(session)
            parentUuids = []
            # содоет ключи в session.params["inputs"]
            for i in range(int(room) + 1):
                # если в 'uuid' есть в session.params["inputs"][str(i)]
                if "parentUuid" in session.params["inputs"][str(i)]:
                    # если 'uuid' нет в словаре с ключем i в списке uuid
                    parentUuids.append(session.params["inputs"][str(i)]["parentUuid"])
            close_date = utcnow().isoformat()[:10]
            for shop_id in shops_id:
                dict_ = {
                    "shop_id": shop_id,
                    "closeDate": close_date,
                    "parentUuids": parentUuids,
                    "user_id": user_id,
                    "x_type": "MOTIVATION_PARENT_UUID",
                }

                GroupUuidAks.objects(
                    shop_id=shop_id,
                    closeDate=close_date,
                    x_type="MOTIVATION_PARENT_UUID",
                ).update(**dict_, upsert=True)

            shops = Shop.objects(uuid__in=shops_id).only("name")
            shop_name = ""
            for shop in shops:
                shop_name += "{}, ".format(shop.name)
            result = [
                {"ДАТА:": close_date},
                {"ГРУППЫ:": "ЗП АКС"},
                {"МАГАЗИН(Ы):".upper(): shop_name},
            ]
            number_ = 1
            for uuid in parentUuids:
                products = Products.objects(group=True, uuid=uuid).first()
                result.append({"{}:".format(number_): products.name})
                number_ += 1

                # pprint(item)
            return result
        # Запрос назначенных групп аксессуаров
        if params["report"] == "get_group_uuid_accessory":
            shops = get_shops(session)
            shop_id_ = shops["shop_id"]
            shop_name = shops["shop_name"]

            documents = (
                GroupUuidAks.objects(
                    shop_id=shop_id_[0], x_type="MOTIVATION_PARENT_UUID"
                )
                .order_by("-closeDate")
                .first()
            )
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
            shops_id = get_shops_uuid_user_id(session)
            motivationUuids = {}
            # содоет ключи в session.params["inputs"]
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
            close_date = utcnow().isoformat()[:10]
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

            shops = Shop.objects(uuid__in=shops_id).only("name")
            shop_name = ""
            for shop in shops:
                shop_name += "{}, ".format(shop.name)

            result = [
                {"Товар доб. мотивации".upper(): ""},
                {"МАГАЗИН(Ы):".upper(): shop_name},
            ]
            for uuid, motivation in motivationUuids.items():
                products = Products.objects(group=False, uuid=uuid).first()
                result.append({"{}:".format(products.name): "{}₱".format(motivation)})

                # pprint(item)
            return result
        # Запрос назначенных товаров доб. мотивации
        if params["report"] == "get_product_ext_motivation":
            shops = get_shops(session)
            shop_id_ = shops["shop_id"]
            shop_name = shops["shop_name"]

            documents = (
                GroupUuidAks.objects(shop_id=shop_id_[0], x_type="MOTIVATION_UUID")
                .order_by("-closeDate")
                .first()
            )
            products = Products.objects(group=False, uuid__in=documents.uuid)
            result = []

            result = [{"Товар доб. мотивации".upper(): ""}, {"МАГАЗИН": shop_name}]
            for uuid, motivation in documents.uuid.items():
                products = Products.objects(group=False, uuid=uuid).first()
                result.append({"{}:".format(products.name): "{}₱".format(motivation)})
            return result
        # Назначить оклады на ТТ
        if params["report"] == "assigning_salary_":
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
            _dict = {"motivation": int(params["motivation"])}

            shops_id = get_shops_uuid_user_id(session)

            result = []
            close_date = utcnow().isoformat()[:10]
            for shop_id in shops_id:
                _dict = {
                    "closeDate": close_date,
                    "motivation": int(params["motivation"]),
                    "user_id": user_id,
                    "shop_id": shop_id,
                    "x_type": "MOTIVATION",
                }
                GroupUuidAks.objects(
                    shop_id=_dict["shop_id"], closeDate=close_date, x_type="MOTIVATION"
                ).update(**_dict, upsert=True)

            shops = Shop.objects(uuid__in=shops_id).only("name")
            shop_name = ""
            for shop in shops:
                shop_name += "{}, ".format(shop.name)

            result = [
                {"ДАТА:": close_date},
                {"СУММА МОТИВАЦИИ:": "{}₱".format(params["motivation"])},
                {"МАГАЗИН(Ы):".upper(): shop_name},
            ]

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
        # Запрос назначенной сум. доплатs к зп
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
            pprint(user)
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

                    result.append(
                        get_total_salary(employee_last_name, sho_id, since_, until_)
                    )
                    # result.append(get_mot_salary(sho_id, since_, until_))
                    # result.append(get_plan_bonus(sho_id, since_, until_))
                    # result.append(get_salary(sho_id, until_))
                    # result.append(get_surcharge(employee_last_name, until_))

                else:
                    result.append({1: 1})
            return result
