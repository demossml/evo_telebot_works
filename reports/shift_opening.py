from arrow import utcnow, get
from bd.model import (
    Session,
    Shift_Opening_Report,
    Plan,
    Employees,
    GetTime,
    Products,
    GroupUuidAks,
)
from .util import (
    generate_plan,
    get_shops,
    get_shops_user_id,
    get_period_day,
    generate_plan_,
)
from .inputs import (
    ShopInput,
    OpenDatePast2Input,
    ReportsShiftOpeningInput,
    AfsInput,
    PeriodDateInput,
)

from pprint import pprint

name = "🕒 ⌛ 💰 📷Открытие ТТ ➡️".upper()
desc = "Собирает данные о открытии смены"
mime = "image"


# Утро:
# 1. Зачекиниться
# 2. Снять с охраны
# 3 Фото кассы (время/дата)
# 4. Фото (ТТ снаружи/внутри)
# 5. Касса ок/не ок (пересчет денег)


# class ShopInput:
#     desc = "Выберите магазин из списка"
#     type = "SELECT"
#
#     def get_options(self, session: Session):
#         _in = ['20210712-1362-4012-8026-5A35685630B2',
#                '20220222-6C28-4069-8006-082BE12BEB32',
#                '20200630-3E0D-4061-80C1-F7897E112F00',
#                '20210923-FB1F-4023-80F6-9ECB3F5A0FA8',
#                '20220201-19C9-40B0-8082-DF8A9067705D',
#                '20220201-8B00-40C2-8002-EF7E53ED1220',
#                '20220201-A55A-40B8-8071-EC8733AFFA8E',
#                '20220202-B042-4021-803D-09E15DADE8A4',
#                '20190411-5A3A-40AC-80B3-8B405633C8BA',
#                '20190327-A48C-407F-801F-DA33CB4FBBE9',
#                '20191117-BF71-40FE-8016-1E7E4A3A4780']
#         output = []
#         for item in get_shops_in(session, _in):
#             output.append({
#                 "id": item["uuid"],
#                 "name": '{} ➡️'.format(item["name"]).upper()
#             })
#
#         return output


# class AfsInput:
#     name = "Подтверждение"
#     desc = "Подтвердите"
#     type = "LOCATION"
#
#     def get_options(self, session: Session):
#         output = [{"name": "чекин".upper()}]
#
#         return output


class PhotoTerritory1Input:
    name = "Магазин"
    desc = "Отправте фото теретори 1 📷".upper()
    type = "PHOTO"


class PhotoTerritory2Input:
    name = "Магазин"
    desc = "Отправте фото теретори 2 📷".upper()
    type = "PHOTO"


class PhotoMRCInput:
    name = "Магазин"
    desc = "Отправте фото МРЦ 📷".upper()
    type = "PHOTO"


class CashRegisterPhotoInput:
    name = "Магазин"
    desc = "Отправте фото кассы 📷".upper()
    type = "PHOTO"


class СabinetsPhotoInput:
    name = "Магазин"
    desc = "Отправте фото шкафов 📷".upper()
    type = "PHOTO"


class showcasePhoto1Input:
    name = "Магазин"
    desc = "Отправте фото витрины 1 📷".upper()
    type = "PHOTO"


class showcasePhoto2Input:
    name = "Магазин"
    desc = "Отправте фото витрины 2 📷".upper()
    type = "PHOTO"


class showcasePhoto3Input:
    name = "Магазин"
    desc = "Отправте фото витрины 3 📷".upper()
    type = "PHOTO"


class CountingMoneyInput:
    desc = "Выберете сходиться/не сходиться (пересчет денег)".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = (
            {"id": "converge", "name": "Сходиться ➡️".upper()},
            {"id": "more", "name": "Больше ➡️".upper()},
            {"id": "less", "name": "Меньше ➡️".upper()},
        )
        return output


class Counting_MoneyInput:
    desc = "Напишите сумму ✍️".upper()
    type = "MESSAGE"


shop_data = (
    "20190411-5A3A-40AC-80B3-8B405633C8BA",
    "20191117-BF71-40FE-8016-1E7E4A3A4780",
    "20231001-6611-407F-8068-AC44283C9196",
    "20190327-A48C-407F-801F-DA33CB4FBBE9",
)


def get_inputs(session: Session):

    # Если входные параметры сессии существуют
    if session.params["inputs"]["0"]:
        # Если тип отчета - "shift_opening_report"
        if session.params["inputs"]["0"]["report"] == "shift_opening_report":
            if "shop" in session.params["inputs"]["0"]:
                if "counting" in session.params["inputs"]["0"]:
                    if session.params["inputs"]["0"]["counting"] == "converge":
                        # Если подсчет равен "converge", возвращаем пустой словарь
                        return {}
                    else:
                        return {
                            "counting_money": Counting_MoneyInput,
                        }

                else:
                    if (
                        session.params["inputs"]["0"]["shop"]
                        == "20220222-6C28-4069-8006-082BE12BEB32"
                    ):
                        return {
                            "location": AfsInput,
                            "cash_register_photo": CashRegisterPhotoInput,
                            "сabinets_photo": СabinetsPhotoInput,
                            "showcase_photo1": showcasePhoto1Input,
                            "showcase_photo2": showcasePhoto2Input,
                            "showcase_photo3": showcasePhoto3Input,
                            "photo_territory_1": PhotoTerritory1Input,
                            "photo_territory_2": PhotoTerritory2Input,
                            "counting": CountingMoneyInput,
                        }
                    if session.params["inputs"]["0"]["shop"] in shop_data:
                        return {
                            "location": AfsInput,
                            "cash_register_photo": CashRegisterPhotoInput,
                            "сabinets_photo": СabinetsPhotoInput,
                            "showcase_photo1": showcasePhoto1Input,
                            "showcase_photo2": showcasePhoto2Input,
                            "showcase_photo3": showcasePhoto3Input,
                            "mrc_photo": PhotoMRCInput,
                            "photo_territory_1": PhotoTerritory1Input,
                            "photo_territory_2": PhotoTerritory2Input,
                            "counting": CountingMoneyInput,
                        }
                    else:
                        return {
                            "shop": ShopInput,
                            "location": AfsInput,
                            "cash_register_photo": CashRegisterPhotoInput,
                            "сabinets_photo": СabinetsPhotoInput,
                            "showcase_photo1": showcasePhoto1Input,
                            "showcase_photo2": showcasePhoto2Input,
                            "photo_territory_1": PhotoTerritory1Input,
                            "photo_territory_2": PhotoTerritory2Input,
                            "counting": CountingMoneyInput,
                        }
            else:
                return {"shop": ShopInput}
        if session.params["inputs"]["0"]["report"] == "get_shift_opening_report":
            if "period" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["period"] == "day":
                    return {}
                else:
                    return {
                        "openDate": OpenDatePast2Input,
                    }
            else:
                return {
                    "shop": ShopInput,
                    # "period": PeriodDateInput,
                }
        if session.params["inputs"]["0"]["report"] == "get_schedules":
            return {}
        if session.params["inputs"]["0"]["report"] == "get_break":
            if "period" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["period"] == "day":
                    return {}
                else:
                    return {
                        "openDate": OpenDatePast2Input,
                    }
            else:
                return {
                    "shop": ShopInput,
                    "period": PeriodDateInput,
                }

    else:
        return {
            "report": ReportsShiftOpeningInput,
        }


def generate(session: Session):
    _dict = {}
    _dict2 = {}
    if session.params["inputs"]["0"]["report"] == "shift_opening_report":
        result = []
        session.params["inputs"]["0"]["distribution_list"] = "yes"
        session.params["inputs"]["0"]["locationData"] = session.params["inputs"]["0"][
            "location"
        ]["data"]
        session.params["inputs"]["0"]["x_type"] = "OPEN"
        params = session.params["inputs"]["0"]

        since = utcnow().replace(hour=3, minute=00).isoformat()
        until = utcnow().replace(hour=20, minute=59).isoformat()

        shop = params["shop"]
        plan_today = Plan.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": shop,
            }
        ).first()
        if plan_today:
            plan = plan_today
        else:
            generate_plan()
            plan = Plan.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": shop,
                }
            ).first()
        Shift_Opening_Report.objects(
            user_id=session.user_id,
            locationData=session.params["inputs"]["0"]["locationData"],
        ).update(**params, upsert=True)
        # Товар доб. мотивации
        documents_mot = (
            GroupUuidAks.objects(shop_id=shop, x_type="MOTIVATION_UUID")
            .order_by("-closeDate")
            .first()
        )
        if documents_mot:
            # products = Products.objects(group=False, uuid__in=documents.uuid)
            dict_mot = {"Товар доб. мотивации".upper(): ""}
            for uuid, motivation in documents_mot.uuid.items():
                products = Products.objects(group=False, uuid=uuid).only("name").first()
                dict_mot.update({"{}:".format(products.name): "{}₱".format(motivation)})
            result.append(dict_mot)
        # Оклад
        documents_salary = (
            GroupUuidAks.objects(shop_id=shop, x_type="SALARY")
            .order_by("-closeDate")
            .first()
        )
        if documents_salary:
            result.append({"ОКЛАД:": "{}₱".format(documents_salary.salary)})
        # Сумма доплаты к зп
        documents_surcharge = (
            GroupUuidAks.objects(
                employee_uuid=str(session.user_id), x_type="ASSING_A_SURCHARGE"
            )
            .order_by("-closeDate")
            .first()
        )

        if documents_surcharge:
            result.append(
                {"СУММА ДОПЛАТЫ:": "{}₱".format(documents_surcharge.surcharge)}
            )
        result.append(
            {
                "План по Fyzzi/Электро".upper(): "{}₱".format(int(plan.sum)),
            }
        )
        if session.params["inputs"]["0"]["counting"] == "converge":
            result.append({"✅Рсхождений по кассе (пересчет денег)".upper(): "НЕТ"})
        else:
            if session.params["inputs"]["0"]["counting"] == "more":
                counting = "+"
            else:
                counting = "-"

            result.append(
                {
                    "🔴Рсхождений по кассе (пересчет денег)".upper(): "{}{}₱".format(
                        counting, session.params["inputs"]["0"]["counting_money"]
                    )
                }
            )

        result.append(
            {
                "✅Смена открыта".upper(): get(params["location"]["data"]).isoformat()[
                    0:16
                ]
            }
        )

        return {}, result

    if session.params["inputs"]["0"]["report"] == "get_shift_opening_report":
        params = session.params["inputs"]["0"]

        shops = get_shops(session)
        shop_id = shops["shop_id"]
        shop_name = shops["shop_name"]

        _dict = {}
        _dict2 = {}
        documents = (
            Shift_Opening_Report.objects(
                __raw__={
                    # 'locationData': {'$gte': since, '$lt': until},
                    "shop": {"$in": shop_id},
                }
            )
            .order_by("-locationData")
            .first()
        )
        if documents:
            for i in documents:
                if "photo" in i:
                    _dict[i] = documents[i]["photo"]
            employees = Employees.objects(lastName=str(documents["user_id"])).first()
            last_name = employees.lastName
            name_ = employees.name
            _dict2.update(
                {
                    "Магазин:".upper(): "{}:".format(shop_name).upper(),
                }
            )
            if "counting" in documents:
                if documents.counting == "converge":
                    _dict2.update(
                        {"✅Рсхождений по кассе (пересчет денег)".upper(): "НЕТ"}
                    )
                else:
                    if documents.counting == "more":
                        counting = "+"
                    else:
                        counting = "-"

                    _dict2.update(
                        {
                            "🔴Рсхождений по кассе (пересчет денег)".upper(): "{}{}₱".format(
                                counting, documents.counting_money
                            )
                        }
                    )

            _dict2.update(
                {
                    "Сотрудник".upper(): name_,
                    "Время открытия TT".upper(): documents["locationData"][0:16],
                    # "Касса".upper(): documents["counting_money"],
                }
            )

            return _dict, [_dict2]
        else:
            return {}, [{"Нет данных".upper(): ""}]

    if session.params["inputs"]["0"]["report"] == "get_schedules":
        shops = get_shops_user_id(session)

        since = utcnow().replace(hour=2).isoformat()
        # _in = [
        #     "20210712-1362-4012-8026-5A35685630B2",
        #     "20220222-6C28-4069-8006-082BE12BEB32",
        #     "20200630-3E0D-4061-80C1-F7897E112F00",
        #     "20210923-FB1F-4023-80F6-9ECB3F5A0FA8",
        #     "20220201-19C9-40B0-8082-DF8A9067705D",
        #     "20220201-8B00-40C2-8002-EF7E53ED1220",
        #     "20220201-A55A-40B8-8071-EC8733AFFA8E",
        #     "20220202-B042-4021-803D-09E15DADE8A4",
        #     "20190411-5A3A-40AC-80B3-8B405633C8BA",
        #     "20190327-A48C-407F-801F-DA33CB4FBBE9",
        #     "20191117-BF71-40FE-8016-1E7E4A3A4780",
        # ]
        result = {}

        for shop in shops:
            pprint(shop["name"])

            # if shop["uuid"] in _in:
            pprint(shop["uuid"])
            documents = GetTime.objects(
                __raw__={"openingData": {"$gte": since}, "shopUuid": shop["uuid"]}
            ).first()
            pprint(documents)

            if documents:
                # pprint(doc['openingData'])
                user_id = str(documents.user_id)
                # pprint(user_id)
                employees = (
                    Employees.objects(lastName=str(user_id)).only("name").first()
                )
                pprint(employees.name)
                if documents["openingData"]:
                    result["{}".format(shop["name"])] = "{} {}".format(
                        employees.name, documents["openingData"][11:16]
                    )
            else:
                result.update({shop["name"]: "ЕЩЕ НЕ ОТКРЫТА!!!".upper()})
        pprint(result)

        return {}, [result]

    if session.params["inputs"]["0"]["report"] == "get_break":
        params = session.params["inputs"]["0"]

        period = get_period_day(session)
        since = period["since"]
        until = period["until"]

        shops = get_shops(session)
        shop_id = shops["shop_id"]
        shop_name = shops["shop_name"]

        documents_break_report = Shift_Opening_Report.objects(
            __raw__={
                "openData": {"$gte": since, "$lt": until},
                "x_type": "BREAK",
                # "break": "open",
                "shop_id": {"$in": shop_id},
            }
        )
        break_data = []
        total_delta = 0
        if len(documents_break_report) > 0:
            for doc in documents_break_report:
                employees = (
                    Employees.objects(lastName=str(doc["user_id"])).only("name").first()
                )
                if "closeDate" in doc:
                    delta = (
                        (get(doc["closeDate"]) - get(doc["openData"])).seconds
                        // 60
                        % 60
                    )
                    total_delta += delta
                    break_data.append(
                        {
                            "перерыв начался".upper(): doc["openData"][:16],
                            "перерыв закончился".upper(): doc["closeDate"][:16],
                            "Время перерыва".upper(): f"{delta} минут",
                        }
                    )
                else:
                    break_data.append(
                        {
                            "перерыв начался".upper(): doc["openData"][:16],
                        }
                    )

            break_data.append(
                {
                    "Магазин:": shop_name,
                    "Продавец:": employees.name,
                    "Итого время перерыва".upper(): f"{total_delta} минут",
                }
            )
        else:
            break_data.append({since[:10]: "Нет данных".upper()})

        return [], break_data
