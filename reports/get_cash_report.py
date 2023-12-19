from bd.model import (
    Shop,
    Products,
    Documents,
    Employees,
    Session,
    ZReopt,
    Plan,
    Surplus,
)
from arrow import utcnow, get
from .util import (
    get_products,
    get_shops,
    get_period_day,
    get_period,
    generate_plan,
    get_total_salary,
    period_first_day_of_the_month,
)
from .inputs import (
    ShopInput,
    ShopAllInput,
    PeriodDateInput,
    OpenDatePastInput,
    CloseDatePastInput,
    ReportsZInput,
    OpenDatePast2Input,
    GroupInput,
    ProductsSaleInput,
    ReportsZReport2Input,
    AfsInput,
    ReportsSurplusInput,
)
from pprint import pprint
import time

name = "🧾Кассовые отчеты ➡️".upper()
desc = ""
mime = "image"


class PlanInput:
    desc = "Напишите план (Fyzzi/Электро)💨💨💨".upper()
    type = "MESSAGE"


class ExecutionPlanInput:
    desc = "Напишите сумму продаж (Fyzzi/Электро)💨💨💨".upper()
    type = "MESSAGE"


class TerminalInput:
    desc = "Напишите расхождения терминала с кассой (0/сумма расхождения)"
    type = "MESSAGE"


class SalaryInput:
    desc = "Напишите оклад".upper()
    type = "MESSAGE"


class SalesAksInput:
    desc = "Напишите сумму продаж по аксессуарам".upper()
    type = "MESSAGE"


class SalaryPromoInput:
    desc = "Напишите сумму премии за продажу мотивационнго товара".upper()
    type = "MESSAGE"


class PhotoList1Input:
    name = "Магазин"
    desc = "Отправте фото лист дня 1 📷".upper()
    type = "PHOTO"


class PhotoList2Input:
    name = "Магазин"
    desc = "Отправте фото лист дня 2📷".upper()
    type = "PHOTO"


class SurplusInput:
    desc = "Напишите сумму излишка"
    type = "MESSAGE"


class CashReceiptInput:
    desc = "Напишите номер чека"
    type = "MESSAGE"


def get_inputs(session: Session):
    period = ["day", "week", "fortnight", "month"]
    if session.params["inputs"]["0"]:
        if session.params["inputs"]["0"]["report"] == "surplus":
            if "report_surplus" in session.params["inputs"]["0"]:
                if (
                    session.params["inputs"]["0"]["report_surplus"]
                    == "register_surplus"
                ):
                    return {
                        "shop_id": ShopInput,
                        "surplus": SurplusInput,
                        "cash_receipt": CashReceiptInput,
                    }
                if session.params["inputs"]["0"]["report_surplus"] == "get_surplus":
                    if "period" in session.params["inputs"]["0"]:
                        if session.params["inputs"]["0"]["period"] == "day":
                            return {}
                        else:
                            return {
                                "openDate": OpenDatePast2Input,
                                "closeDate": CloseDatePastInput,
                            }
                    else:
                        return {
                            "shop": ShopInput,
                            "period": PeriodDateInput,
                        }

            else:
                return {"report_surplus": ReportsSurplusInput}
        if session.params["inputs"]["0"]["report"] == "detailed_report":
            if "report_z" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["report_z"] == "z_report":
                    return {
                        "shop": ShopInput,
                        "location": AfsInput,
                        # "plan": PlanInput,
                        "executionPlan": ExecutionPlanInput,
                        "terminal": TerminalInput,
                        "salary": SalaryInput,
                        "salesAksInput": SalesAksInput,
                        "salaryPromo": SalaryPromoInput,
                    }
                if session.params["inputs"]["0"]["report_z"] == "get_z_report":
                    if "period" in session.params["inputs"]["0"]:
                        if session.params["inputs"]["0"]["period"] == "day":
                            return {}
                        else:
                            return {
                                "openDate": OpenDatePastInput,
                            }
                    else:
                        return {
                            "shop": ShopInput,
                            "period": PeriodDateInput,
                        }
                if session.params["inputs"]["0"]["report_z"] == "z_photo":
                    return {
                        # "shop": ShopInput,
                        "photoList1": PhotoList1Input,
                        "photoList2": PhotoList2Input,
                    }

            else:
                return {"report_z": ReportsZReport2Input}

        if session.params["inputs"]["0"]["report"] == "report_cash_outcome":
            # period = ["day", "week", "fortnight", "month"]
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
                    "shop": ShopAllInput,
                    "period": PeriodDateInput,
                }

        if session.params["inputs"]["0"]["report"] == "report_cash_income":
            # period = ["day", "week", "fortnight", "month"]
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
                    "shop": ShopInput,
                    "period": PeriodDateInput,
                }

        if session.params["inputs"]["0"]["report"] == "get_check":
            if "period" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["period"] == "day":
                    return {
                        "shop": ShopInput,
                        "group": GroupInput,
                        "productsUuid": ProductsSaleInput,
                    }
                else:
                    return {
                        "openDate": OpenDatePast2Input,
                        "shop": ShopInput,
                        "group": GroupInput,
                        "productsUuid": ProductsSaleInput,
                    }
            else:
                return {"period": PeriodDateInput}
    else:
        return {
            "report": ReportsZInput,
        }


def generate(session: Session):
    global sum_payment_category, dict_
    params = session.params["inputs"]["0"]

    result = []
    payment_category = {
        "1": "Инкассация".upper(),
        "2": "Оплата поставщику".upper(),
        "3": "Оплата услуг".upper(),
        "4": "Аренда".upper(),
        "5": "Заработная плата".upper(),
        "6": "Прочее".upper(),
    }
    shops_id_2 = {
        "20200630-3E0D-4061-80C1-F7897E112F00": "20220430-A472-40B8-8077-2EE96318B7E7",
        "20220201-19C9-40B0-8082-DF8A9067705D": "20220501-9ADF-402C-8012-FB88547F6222",
        "20220222-6C28-4069-8006-082BE12BEB32": "20220601-4E97-40A5-801B-1A29127AFA8B",
        "20210923-FB1F-4023-80F6-9ECB3F5A0FA8": "20220501-11CA-40E0-8031-49EADC90D1C4",
        # '20220202-B042-4021-803D-09E15DADE8A4': '20220501-CB2E-4020-808C-E3FD3CB1A1D4',
        "20210712-1362-4012-8026-5A35685630B2": "20220501-DDCF-409A-8022-486441F27458",
        "20220201-8B00-40C2-8002-EF7E53ED1220": "20220501-3254-40E5-809E-AC6BB204D373",
        "20220201-A55A-40B8-8071-EC8733AFFA8E": "20220501-4D25-40AD-80DA-77FAE02A007E",
        "20220202-B042-4021-803D-09E15DADE8A4": "20230214-33E5-4085-80A3-28C177E34112",
    }

    if "report_surplus" in session.params["inputs"]["0"]:
        if session.params["inputs"]["0"]["report_surplus"] == "register_surplus":
            dict_ = {
                "shop_id": params["shop_id"],
                "surplus": params["surplus"],
                "cash_receipt": params["cash_receipt"],
                "user_id": session.user_id,
                "closeDate": utcnow().isoformat(),
            }
            Surplus.objects(
                closeDate=dict_["closeDate"], shop_id=dict_["shop_id"]
            ).update(**dict_, upsert=True)

            result_message = {
                "1 TT:": [i["name"] for i in Shop.objects(uuid=params["shop_id"])][0],
                "2 Излишек": "{} {}".format(params["surplus"], "₽"),
                "3 ПРОДАВЕЦ": [
                    i["name"] for i in Employees.objects(lastName=str(session.user_id))
                ][0],
                "4 Дата": utcnow().shift(hours=3).isoformat()[0:16],
                "5 Номер чека:": params["cash_receipt"],
            }
            return {}, [result_message]
        if session.params["inputs"]["0"]["report_surplus"] == "get_surplus":
            period = get_period_day(session)
            since = period["since"]
            until = period["until"]

            shops = get_shops(session)
            shop_id = shops["shop_id"]
            shop_name = shops["shop_name"]

            pprint(f"{since}/{until}/{shop_name}")
            documents = Surplus.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": {"$in": shop_id},
                }
            )
            len_data = len(documents)
            pprint(f"{since}/{until}/{shop_name}/{len_data}")

            result = []
            if len(documents) > 0:
                sum_surplus = 0
                for item in documents:
                    dict_ = {
                        "1 TT:": shop_name,
                        "2 Излишек": "{} {}".format(item["surplus"], "₽"),
                        "3 ПРОДАВЕЦ": [
                            i["name"]
                            for i in Employees.objects(lastName=str(item["user_id"]))
                        ][0],
                        "4 Дата": item["closeDate"][0:16],
                        "5 Номер чека:": item["cash_receipt"],
                    }
                    sum_surplus += int(item["surplus"])
                    result.append(dict_)
                result.append({"Итого:": sum_surplus})

                return {}, result
            else:
                return {}, [{shop_name: f"НЕТ ДАННЫХ {since[:10]}/{until[:10]}"}]
    if "report_z" in session.params["inputs"]["0"]:
        if session.params["inputs"]["0"]["report_z"] == "z_report":
            session.params["inputs"]["0"]["distribution_list"] = "yes"
            session.params["inputs"]["0"]["locationData"] = session.params["inputs"][
                "0"
            ]["location"]["data"]
            session.params["inputs"]["0"]["user_id"] = session.user_id
            since = utcnow().replace(hour=3, minute=00).isoformat()
            until = utcnow().replace(hour=20, minute=59).isoformat()

            plan_today = Plan.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": session.params["inputs"]["0"]["shop"],
                }
            ).first()
            plan = {}

            if plan_today:
                pprint("plan yes")
                plan = plan_today
            else:
                pprint("plan no")
                generate_plan()
                # time.sleep(10)

                plan = Plan.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": session.params["inputs"]["0"]["shop"],
                    }
                ).first()
                pprint(plan)

            if int(session.params["inputs"]["0"]["executionPlan"]) >= plan.sum:
                planSalary = 250
            else:
                planSalary = 0
            session.params["inputs"]["0"]["planSalary"] = planSalary

            aksSalary = (
                round(
                    (int(session.params["inputs"]["0"]["salesAksInput"]) / 100 * 5) / 10
                )
                * 10
            )
            session.params["inputs"]["0"]["aksSalary"] = int(aksSalary)

            number = ZReopt.objects().order_by("-number").first()
            if number:
                session.params["inputs"]["0"]["number"] = number.number + 1
            else:
                session.params["inputs"]["0"]["number"] = 1

            params = session.params["inputs"]["0"]
            ZReopt.objects(
                locationData=session.params["inputs"]["0"]["locationData"],
                shop=session.params["inputs"]["0"]["shop"],
            ).update(**params, upsert=True)

            shop_name = Shop.objects(uuid=params["shop"]).only("name").first()
            employees = (
                Employees.objects(lastName=str(session.user_id)).only("name").first()
            )

            salary = int(session.params["inputs"]["0"]["salary"])

            planSalary = int(session.params["inputs"]["0"]["planSalary"])
            aksSalary = int(session.params["inputs"]["0"]["aksSalary"])
            salaryPromo = int(session.params["inputs"]["0"]["salaryPromo"])
            salary_total = salary + planSalary + aksSalary + salaryPromo
            _dict = {
                "Дата/Время:": get(params["location"]["data"]).isoformat()[0:16],
                "Расхождения терминала с кассой:": "{} ₽".format(
                    session.params["inputs"]["0"]["terminal"]
                ),
                "Оклад:": "{} ₽".format(session.params["inputs"]["0"]["salary"]),
                "План(Fyzzi/Электро):": "{} ₽".format(plan.sum),
                "Зп план:": "{} ₽".format(session.params["inputs"]["0"]["planSalary"]),
                "Зп акс:": "{} ₽".format(session.params["inputs"]["0"]["aksSalary"]),
                "Зп мотивация:": "{} ₽".format(
                    session.params["inputs"]["0"]["salaryPromo"]
                ),
                "Итого зп:": "{} ₽".format(salary_total),
                "ТТ:": shop_name.name,
                "Продавец:": employees.name,
            }
            _dict1 = {}
            return _dict1, [_dict]
        if session.params["inputs"]["0"]["report_z"] == "z_photo":
            params = session.params["inputs"]["0"]
            pprint(params)

            documents = (
                ZReopt.objects(
                    __raw__={
                        "user_id": int(session.user_id),
                    }
                ).order_by("-number")
                # .only("number")
                .first()
            )

            ZReopt.objects(number=documents.number).update(**params, upsert=True)
            shop_name = [i.name for i in Shop.objects(uuid=documents.shop)]
            employees = [
                i.name for i in Employees.objects(lastName=str(session.user_id))
            ]

            _dict = {
                "Дата/Время:": utcnow().isoformat()[0:16],
                "ТТ:": shop_name[0],
                "Продавец:": employees[0],
                "Фото загруженны": 2,
            }
            _dict1 = {}
            return _dict1, [_dict]
        if session.params["inputs"]["0"]["report_z"] == "get_z_report":
            params = session.params["inputs"]["0"]

            shop = Shop.objects(uuid=params["shop"]).first()

            period = get_period_day(session)
            since = period["since"]
            until = period["until"]

            result = []

            documents_z_report = (
                ZReopt.objects(
                    __raw__={
                        "locationData": {"$gte": since, "$lt": until},
                        "shop": shop.uuid,
                    }
                )
                .order_by("-locationData")
                .first()
            )

            dict_1 = {
                "photo_territory_1": documents_z_report["photoList1"]["photo"],
                "photo_territory_2": documents_z_report["photoList2"]["photo"],
            }

            employees = Employees.objects(
                lastName=str(documents_z_report.user_id)
            ).first()

            if employees:
                employeeName = employees.name
            else:
                employeeName = ["Unknown "]
            salary_total = (
                int(documents_z_report.salary)
                + int(documents_z_report.planSalary)
                + int(documents_z_report.aksSalary)
                + int(documents_z_report.salaryPromo)
            )

            if shop.uuid in shops_id_2:
                shops_id = [shop.uuid, shops_id_2[shop.uuid]]
            else:
                shops_id = [shop.uuid]
            pprint(shops_id)
            register = 1
            for shop_id in shops_id:
                x_type = ["FPRINT", "CASH_OUTCOME", "CASH_INCOME", "ACCEPT"]
                documents = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": shop_id,
                        "x_type": {"$in": x_type},
                    }
                )

                _dict = {}
                summ_salary = 0
                for doc in documents:
                    _dict["КАССА:"] = str(register)
                    if doc["x_type"] == "FPRINT":
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "FPRINT_Z_REPORT":
                                _dict["{} Магазин:".format("1").upper()] = [
                                    i.name for i in Shop.objects(uuid=doc["shop_id"])
                                ][0]
                                _dict["{} ДАТА/ВРЕМЯ ЗАКРЫТИЯ:".format("2")] = (
                                    get(doc["closeDate"])
                                    .shift(hours=3)
                                    .isoformat()[0:16]
                                )

                                employees = Employees.objects(
                                    uuid=doc["openUserUuid"]
                                ).first()
                                last_name = employees.lastName
                                name_ = employees.name
                                _dict["{} ПРОДАВЕЦ:".format("3")] = "{} {}:".format(
                                    last_name, name_
                                ).upper()

                                _dict[
                                    "{} ПРОДАЖИ {}:".format(
                                        "4", trans["sales"]["sections"][1]["name"]
                                    )
                                ] = "{}₽".format(trans["sales"]["sections"][1]["value"])
                                _dict[
                                    "{} ПРОДАЖИ {}:".format(
                                        "5", trans["sales"]["sections"][2]["name"]
                                    )
                                ] = "{}₽".format(trans["sales"]["sections"][2]["value"])
                                _dict[
                                    "{} ВОЗВРАТЫ {}:".format(
                                        "6", trans["salesBack"]["sections"][1]["name"]
                                    )
                                ] = "{}₽".format(
                                    trans["salesBack"]["sections"][1]["value"]
                                )
                                _dict[
                                    "{} ВОЗВРАТЫ {}:".format(
                                        "7", trans["salesBack"]["sections"][2]["name"]
                                    )
                                ] = "{}₽".format(
                                    trans["salesBack"]["sections"][2]["value"]
                                )
                                _dict["{} ИТОГО ПРОДАЖИ:".format("8")] = "{}₽".format(
                                    trans["sales"]["summ"]
                                )
                                _dict[
                                    "{} НАЛИЧНЫМИ В КАССЕ:".format("9")
                                ] = "{}₽".format(trans["cash"])
                                _dict["{} ИТОГО ВЫПЛАТЫ:".format("10")] = "{}₽".format(
                                    trans["cashOut"]
                                )

                    if doc["x_type"] == "CASH_OUTCOME":
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "CASH_OUTCOME":
                                _dict[
                                    "ВЫПЛАТА ЧЕК №{}".format(doc["number"])
                                ] = "{}₽/{}".format(
                                    trans["sum"],
                                    payment_category[str(trans["paymentCategoryId"])],
                                )
                                if trans["paymentCategoryId"] == 5:
                                    summ_salary += trans["sum"]

                    if doc["x_type"] == "CASH_INCOME":
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "CASH_INCOME":
                                _dict[
                                    "ВНЕСЕНИЕ ЧЕК №{}".format(doc["number"])
                                ] = "{}₽".format(trans["sum"])

                    if doc["x_type"] == "ACCEPT":
                        for trans in doc["transactions"]:
                            _dict["ПРИНЯТО ТОВАРА НА"] = "{}₽".format(doc["closeSum"])

                result.append(_dict)
                register += 1

            result.append(
                {
                    "Данные из Z отчета продавеца".upper(): " ",
                    "Дата/Время:": documents_z_report.locationData[0:16],
                    "Расхождения терминала с кассой:": "{} ₽".format(
                        documents_z_report.terminal
                    ),
                    "Оклад:": "{} ₽".format(documents_z_report.salary),
                    # 'План(Fyzzi/Электро):': documents.plan,
                    "Зп план:": "{} ₽".format(documents_z_report.planSalary),
                    "Зп акс:": "{} ₽".format(int(documents_z_report.aksSalary)),
                    "Зп мотивация:": "{} ₽".format(documents_z_report.salaryPromo),
                    "Итого зп:": "{} ₽".format(round(salary_total, 0)),
                    "ТТ:": shop.name,
                    "Продавец:": employeeName,
                }
            )
            total_salary = get_total_salary(
                str(documents_z_report.user_id), shop.uuid, since, until
            )
            if total_salary:
                result.append(
                    {
                        "Данные из Z отчета кассы".upper(): " ",
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
                        "Итго зарплата".upper(): "{}₱".format(
                            total_salary["total_salary"]
                        ),
                        "СРАВНЕНИЕ ЗП": "{}₱".format(
                            total_salary["total_salary"] - summ_salary
                        ),
                    }
                )

            return dict_1, result
    else:
        if session.params["inputs"]["0"]["report"] == "detailed_report":
            period = get_period_day(session)

            since = period["since"]
            until = period["until"]

            shops = get_shops(session)
            shop_id = shops["shop_id"]
            shop_name = shops["shop_name"]

            register = 1
            for shop_uuid in shop_id:
                x_type = ["FPRINT", "CASH_OUTCOME", "CASH_INCOME", "ACCEPT"]
                documents = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": shop_uuid,
                        "x_type": {"$in": x_type},
                    }
                )
                _dict = {}

                for doc in documents:
                    _dict["КАССА:"] = str(register)
                    if doc["x_type"] == "FPRINT":
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "FPRINT_Z_REPORT":
                                _dict["✅{} Магазин:".format("1").upper()] = [
                                    i.name for i in Shop.objects(uuid=doc["shop_id"])
                                ][0]
                                _dict["✅{} ДАТА/ВРЕМЯ ЗАКРЫТИЯ:".format("2")] = (
                                    get(doc["closeDate"])
                                    .shift(hours=3)
                                    .isoformat()[0:16]
                                )

                                employees = Employees.objects(
                                    uuid=doc["openUserUuid"]
                                ).first()
                                last_name = employees.lastName
                                name_ = employees.name
                                _dict["✅{} ПРОДАВЕЦ:".format("3")] = "{} {}:".format(
                                    last_name, name_
                                ).upper()

                                _dict[
                                    "✅{} ПРОДАЖИ {}:".format(
                                        "4", trans["sales"]["sections"][1]["name"]
                                    )
                                ] = "{}₽".format(trans["sales"]["sections"][1]["value"])
                                _dict[
                                    "✅{} ПРОДАЖИ {}:".format(
                                        "5", trans["sales"]["sections"][2]["name"]
                                    )
                                ] = "{}₽".format(trans["sales"]["sections"][2]["value"])
                                _dict[
                                    "✅{} ВОЗВРАТЫ {}:".format(
                                        "6", trans["salesBack"]["sections"][1]["name"]
                                    )
                                ] = "{}₽".format(
                                    trans["salesBack"]["sections"][1]["value"]
                                )
                                _dict[
                                    "✅{} ВОЗВРАТЫ {}:".format(
                                        "7", trans["salesBack"]["sections"][2]["name"]
                                    )
                                ] = "{}₽".format(
                                    trans["salesBack"]["sections"][2]["value"]
                                )
                                _dict["✅{} ИТОГО ПРОДАЖИ:".format("8")] = "{}₽".format(
                                    trans["sales"]["summ"]
                                )
                                _dict[
                                    "✅{} НАЛИЧНЫМИ В КАССЕ:".format("9")
                                ] = "{}₽".format(trans["cash"])
                                _dict["✅{} ИТОГО ВЫПЛАТЫ:".format("10")] = "{}₽".format(
                                    trans["cashOut"]
                                )

                    if doc["x_type"] == "CASH_OUTCOME":
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "CASH_OUTCOME":
                                _dict[
                                    "✅ВЫПЛАТА ЧЕК №{}".format(doc["number"])
                                ] = "{}₽/{}".format(
                                    trans["sum"],
                                    payment_category[str(trans["paymentCategoryId"])],
                                )

                    if doc["x_type"] == "CASH_INCOME":
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "CASH_INCOME":
                                _dict[
                                    "✅ВНЕСЕНИЕ ЧЕК №{}".format(doc["number"])
                                ] = "{}₽".format(trans["sum"])

                    if doc["x_type"] == "ACCEPT":
                        for trans in doc["transactions"]:
                            _dict["✅ПРИНЯТО ТОВАРА НА"] = "{}₽".format(doc["closeSum"])

                # _dict = dict(OrderedDict(sorted(_dict.items(), key=lambda t: -t[1])))

                result.append(_dict)
                register += 1
            return {}, result
        if session.params["inputs"]["0"]["report"] == "report_cash_outcome":
            shops = get_shops(session)
            shops_id = shops["shop_id"]
            shop_name = shops["shop_name"]

            period = get_period(session)
            since = period["since"]
            until = period["until"]
            result = []
            sum_payment_category = {"sum": 0}
            dict_ = {}

            for shop_id in shops_id:
                shops_uuid = [shop_id]
            if shop_id in shops_id_2:
                shops_uuid.append(shops_id_2[shop_id])
            register = 1

            for shop_uuid in shops_uuid:
                x_type = ["CASH_OUTCOME"]
                documents = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": shop_uuid,
                        "x_type": {"$in": x_type},
                    }
                )

                for doc in documents:
                    if doc["x_type"] == "CASH_OUTCOME":
                        check = {}
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "CASH_OUTCOME":
                                employees = Employees.objects(
                                    uuid=doc["openUserUuid"]
                                ).first()
                                if employees:
                                    last_name = employees.lastName
                                    name_ = employees.name
                                else:
                                    name_ = " "
                                    last_name = " "
                                pprint(trans["id"])
                                pprint(payment_category[str(trans["id"])])
                                result.append(
                                    {
                                        "№ чека:".upper(): doc["number"],
                                        "Дата:".upper(): trans["creationDate"][:19],
                                        "Пордавец:".upper(): "{} {}:".format(
                                            last_name, name_
                                        ).upper(),
                                        "Категории платежа:".upper(): payment_category[
                                            str(trans["paymentCategoryId"])
                                        ],
                                        "Сумма:".upper(): "{} ₽".format(trans["sum"]),
                                    }
                                )
                                sum_payment_category["sum"] += trans["sum"]
                                if (
                                    str(trans["paymentCategoryId"])
                                    in sum_payment_category
                                ):
                                    sum_payment_category[
                                        str(trans["paymentCategoryId"])
                                    ] += trans["sum"]
                                else:
                                    sum_payment_category[
                                        str(trans["paymentCategoryId"])
                                    ] = trans["sum"]

            _dict = {
                "Итого:".upper(): "⬇️⬇️⬇️⬇️⬇️️⬇️️⬇️️⬇️️️",
                "Магазин:".upper(): shop_name,
                "Начало пириода:".upper(): since[0:10],
                "Окончание пириода:".upper(): until[0:10],
            }
            for k, v in sum_payment_category.items():
                if k != "sum":
                    _dict.update({payment_category[k]: "{} ₽".format(v)})
            _dict.update({"Сумма:".upper(): "{} ₽".format(sum_payment_category["sum"])})
            result.append(_dict)

            return {}, result
        if session.params["inputs"]["0"]["report"] == "report_cash_income":
            shops = get_shops(session)
            shop_id = shops["shop_id"]
            shop_name = shops["shop_name"]

            period = get_period(session)
            since = period["since"]
            until = period["until"]

            result = []
            sum_ = 0

            for shop_uuid in shop_id:
                x_type = ["CASH_INCOME"]
                documents = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": shop_uuid,
                        "x_type": {"$in": x_type},
                    }
                )

                for doc in documents:
                    if doc["x_type"] == "CASH_INCOME":
                        for trans in doc["transactions"]:
                            if trans["x_type"] == "CASH_OUTCOME":
                                employees = Employees.objects(
                                    uuid=trans["userUuid"]
                                ).first()
                                last_name = employees.lastName
                                name_ = employees.name
                                result.append(
                                    {
                                        "№ чека:".upper(): doc["number"],
                                        "Дата:".upper(): trans["creationDate"][:19],
                                        "Пордавец:".upper(): "{} {}:".format(
                                            last_name, name_
                                        ).upper(),
                                        "Категории платежа:".upper(): payment_category[
                                            str(trans["id"])
                                        ],
                                        "Сумма:".upper(): "{} ₽".format(trans["sum"]),
                                    }
                                )
                                sum_ += trans["sum"]

            _dict = {
                "Итого:".upper(): "⬇️⬇️⬇️⬇️⬇️️⬇️️⬇️️⬇️️️",
                "✅Магазин:": shop.name,
                "✅Начало пириода:": since[0:10],
                "✅Окончание пириода:": until[0:10],
                "✅Сумма:": "{}₽".format(sum_),
            }
            result.append(_dict)
            return {}, result
        if session.params["inputs"]["0"]["report"] == "get_check":
            period = get_period_day(session)

            since = period["since"]
            until = period["until"]

            shop = params["shop"]
            uuid = params["productsUuid"]

            payment_type = {
                "CARD": "Банковской картой",
                "ADVANCE": "Предоплатой (зачетом аванса)",
                "CASH": "Наличными средствами",
                "COUNTEROFFER": "Встречным предоставлением",
                "CREDIT": "Постоплатой (в кредит)",
                "ELECTRON": "Безналичными средствами",
                "UNKNOWN": "Неизвестно. По-умолчанию",
            }

            documents = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop,
                    "x_type": "SELL",
                    "transactions.commodityUuid": uuid,
                }
            )
            result = []

            for doc in documents:
                dict_ = {"ЧЕК №:": doc["number"], "ДАТА:": since[0:10]}
                for trans in doc["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        dict_.update(
                            {
                                "{}".format(trans["commodityName"]): "{} {}".format(
                                    trans["quantity"], "шт."
                                )
                            }
                        )
                    if trans["x_type"] == "PAYMENT":
                        # print(trans['paymentType'])
                        dict_.update(
                            {
                                "ФОРМА ОПЛАТЫ:": payment_type[trans["paymentType"]],
                                "СУММА:": "{} {}".format(doc["closeSum"], "₽"),
                            }
                        )

                result.append(dict_)

            return {}, result
