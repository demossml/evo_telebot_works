from bd.model import Products, Documents, Session, Shop, MarriageWarehouse, Employees
from .util import (
    get_shops,
    get_commodity_balances,
    format_sell_groups,
    period_to_date,
    get_period_day,
    gather_statistics_name,
    gather_statistics_uuid,
    get_commodity_balances_all,
    get_sale_uuid,
    get_commodity_balances_p,
)
from pprint import pprint
from arrow import get, utcnow
from collections import OrderedDict
import time


from .inputs import (
    ReportCommodityInput,
    GroupInput,
    PeriodDateInput,
    CloseDatePastInput,
    ShopInput,
    OpenDatePast2Input,
    DocumentsAcceptInput,
    ReportsAcceptInput,
    ShopAllInput,
    СounterpartyInput,
    ProductElectroInput,
    ReportsMarriageInput,
)

name = "™️ Tоварные отчеты ➡️".upper()
desc = ""
mime = "text"


class PackageInput:
    name = "Выберит есть упаковка"
    desc = "Выберит есть упаковка📦™️➡️".upper()
    type = "SELECT"

    def get_options(self, session: Session):
        output = ({"id": "yes", "name": "ДА"}, {"id": "no", "name": "НЕТ"})

        return output


class PhotoProductInput:
    name = "Отправте фото товара"
    desc = "Отправте фото товара 📷📸➡️".upper()
    type = "PHOTO"


class DefectInput:
    desc = "Напишите опишите дефект ⚠️➡️".upper()
    type = "MESSAGE"


class СonsignmentInput:
    desc = "Напишите номер накладной"
    type = "MESSAGE"


class TransferInput:
    desc = "Накладная на перемещения создана"
    type = "MESSAGE_2"

    def get_options(self, session: Session):
        result = []
        output = ({"id": "yes", "name": "Да"}, {"id": "no", "name": "Нет"})
        # shop_uuid = [i['uuid'] for i in get_shops(session)]
        # pprint(shop_uuid)
        # params = session.params["inputs"]['0']
        # if params['shop'] == 'all':
        #     Marriage = MarriageWarehouse.objects(__raw__={
        #         'availability': 'yes',
        #         'shop': {'$in': shop_uuid},
        #     })
        # else:
        #     Marriage = MarriageWarehouse.objects(__raw__={
        #         'availability': 'yes',
        #         'shop': params['shop']
        #     })
        # if len(Marriage) == 0:
        #     result.append({'Брака': 'нет'})
        # for item in Marriage:
        #     product = Products.objects(__raw__={
        #         'uuid': item['product']
        #     })
        #     product_name = [i['name'] for i in product]
        #     employee_name = [i['name'] for i in Employees.objects(lastName=item['user_id'])]
        #     shop_name = [i['name'] for i in Shop.objects(uuid=item['shop'])]
        #     # pprint(product_name[0])
        #     if len(product_name) > 0:
        #         result.append({
        #             'ТТ:': shop_name[0],
        #             'Дата:': item['closeDate'][0:16],
        #             'Наименование:': product_name[0],
        #             'Дефект:': item['defect'],
        #             'Упаковка:': item['package']
        #         })

        return output


def get_inputs(session: Session):
    # Периоды для запроса зарплатных данных
    period = ["day", "week", "fortnight", "month"]
    if session.params["inputs"]["0"]:
        if session.params["inputs"]["0"]["report"] == "marriage":
            if "report_marriage" in session.params["inputs"]["0"]:
                if (
                    session.params["inputs"]["0"]["report_marriage"]
                    == "marriage_registration"
                ):
                    return {
                        "shop": ShopInput,
                        "product": ProductElectroInput,
                        "package": PackageInput,
                        "photo": PhotoProductInput,
                        "defect": DefectInput,
                    }
                if session.params["inputs"]["0"]["report_marriage"] == "get_marriage":
                    if "period" in session.params["inputs"]["0"]:
                        if session.params["inputs"]["0"]["period"] == "day":
                            return {}
                        else:
                            return {
                                "openDate": OpenDatePast2Input,
                                "closeDate": CloseDatePastInput,
                            }
                    return {"shop": ShopInput, "period": PeriodDateInput}
            else:
                return {"report_marriage": ReportsMarriageInput}

        if session.params["inputs"]["0"]["report"] == "get_commodity_balances":
            return {
                "shop": ShopInput,
                "group": GroupInput,
            }
        if session.params["inputs"]["0"]["report"] == "order_constructor":
            return {
                "shop": ShopInput,
                "counterparty": СounterpartyInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePast2Input,
                "closeDate": CloseDatePastInput,
            }
        if session.params["inputs"]["0"]["report"] == "get_accept":
            if "period" in session.params["inputs"]["0"]:
                if session.params["inputs"]["0"]["period"] == "day":
                    return {"shop": ShopInput, "number": DocumentsAcceptInput}

                else:
                    return {
                        "shop": ShopInput,
                        "openDate": OpenDatePast2Input,
                        "closeDate": CloseDatePastInput,
                        "number": DocumentsAcceptInput,
                    }
            else:
                return {"report_a_w": ReportsAcceptInput, "period": PeriodDateInput}
        if session.params["inputs"]["0"]["report"] == "get_product_not_for_sale":
            return {
                "shop": ShopAllInput,
                "group": GroupInput,
                "period": PeriodDateInput,
                "openDate": OpenDatePast2Input,
            }

    else:
        return {"report": ReportCommodityInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]

    if "report_marriage" in session.params["inputs"]["0"]:
        if session.params["inputs"]["0"]["report_marriage"] == "marriage_registration":
            session.params["inputs"]["0"]["availability"] = "yes"
            session.params["inputs"]["0"]["user_id"] = str(session["user_id"])
            data = utcnow().isoformat()
            session.params["inputs"]["0"]["closeDate"] = data
            params = session.params["inputs"]["0"]
            marriage = MarriageWarehouse.objects().first()
            if marriage:
                number = MarriageWarehouse.objects().order_by("-number").first()
                session.params["inputs"]["0"]["number"] = number.number + 1
            else:
                session.params["inputs"]["0"]["number"] = 1

            MarriageWarehouse.objects(closeDate=data).update(**params, upsert=True)
            shop_uuid = session.params["inputs"]["0"]["shop"]
            shop_name = [i["name"] for i in Shop.objects(uuid=shop_uuid)]
            product = Products.objects(
                __raw__={
                    "shop_id": shop_uuid,
                    "uuid": session.params["inputs"]["0"]["product"],
                }
            )
            product_name = [i["name"] for i in product]

            _dict = {
                "№".upper(): session.params["inputs"]["0"]["number"],
                "ТТ:".upper(): shop_name[0],
                "Дата:".upper(): session.params["inputs"]["0"]["closeDate"][0:16],
                "Наименование:".upper(): product_name[0],
                "Дефект:".upper(): session.params["inputs"]["0"]["defect"],
                "Упаковка:".upper(): session.params["inputs"]["0"]["package"],
            }

            return [_dict]
        if session.params["inputs"]["0"]["report_marriage"] == "get_marriage":
            params = session.params["inputs"]["0"]
            period = get_period_day(session)
            since = period["since"]
            until = period["until"]
            result = []
            dict_ = {}
            Marriage = MarriageWarehouse.objects(
                __raw__={
                    "availability": "yes",
                    "shop": params["shop"],
                    "closeDate": {"$gte": since, "$lt": until},
                }
            )
            for item in Marriage:
                product = Products.objects(
                    __raw__={"shop_id": item["shop"], "uuid": item["product"]}
                )
                product_name = [i["name"] for i in product]
                employee_name = [
                    i["name"] for i in Employees.objects(lastName=item["user_id"])
                ]
                shop_name = [i["name"] for i in Shop.objects(uuid=item["shop"])]
                result.append(
                    {
                        "№".upper(): item["number"],
                        "ТТ:": shop_name[0],
                        "Дата:": item["closeDate"][0:16],
                        "Наименование:": product_name[0],
                        "Дефект:": item["defect"],
                        "Упаковка:": item["package"],
                    }
                )
                if product_name[0] in dict_:
                    dict_[product_name[0]] += 1
                else:
                    dict_[product_name[0]] = 1
            result.append(dict_)
            return result

    else:
        if params["report"] == "get_commodity_balances":
            x_type = ("SELL", "PAYBACK", "ACCEPT")
            result = []
            shops = get_shops(session)
            shop_id = shops["shop_id"]
            shop_name = shops["shop_name"]

            for shop_uuid in shop_id:
                if "group" in params:
                    if params["group"] == "all":
                        products = Products.objects(
                            __raw__={
                                "shop_id": shop_uuid,
                            }
                        )
                        group_name = "Все"
                    else:
                        products = Products.objects(
                            __raw__={
                                "shop_id": shop_uuid,
                                "parentUuid": params["group"],
                            }
                        )
                        porod = Products.objects(
                            uuid=params["group"], group__exact=True
                        ).first()
                        group_name = porod.name
                products_uuid = [element.uuid for element in products]

                result.append({"Магазин:": shop_name, "Группа": group_name})

                for uuid in products_uuid:
                    # product = Products.objects(uuid=uuid, group__exact=False).first()
                    documents = (
                        Documents.objects(
                            __raw__={
                                "shop_id": shop_uuid,
                                "x_type": {"$in": x_type},
                                "transactions.commodityUuid": uuid,
                            }
                        )
                        .order_by("-closeDate")
                        .first()
                    )
                    # pprint(documents)

                    if documents is not None:
                        _dict = {}

                        for trans in documents["transactions"]:
                            if trans["x_type"] == "REGISTER_POSITION":
                                if trans["commodityUuid"] == uuid:
                                    _dict.update(
                                        {
                                            "1 Наименование:": trans["commodityName"],
                                            "2 Цена поставки:": "{} ₱".format(
                                                trans["costPrice"]
                                            ),
                                            "3 Цена продажи:": "{} ₱".format(
                                                trans["price"]
                                            ),
                                        }
                                    )

                                    if documents.x_type == "SELL":
                                        _dict["4 Количество"] = "{} {}".format(
                                            trans["balanceQuantity"]
                                            - trans["quantity"],
                                            trans["measureName"],
                                        )

                                    if documents.x_type == "PAYBACK":
                                        _dict["4 Количество"] = "{} {}".format(
                                            trans["balanceQuantity"]
                                            + trans["quantity"],
                                            trans["measureName"],
                                        )

                                    if documents.x_type == "ACCEPT":
                                        _dict["4 Количество"] = "{} {}".format(
                                            trans["balanceQuantity"],
                                            trans["measureName"],
                                        )

                        result.append(_dict)
                    else:
                        product = Products.objects(
                            uuid=uuid, group__exact=False
                        ).first()
                        result.append(
                            {
                                "1 Наименование:": product["name"],
                                "2 Цена поставки:": "{} ₱".format(product["costPrice"]),
                                "3 Цена продажи:": "{} ₱".format(product["price"]),
                                "4 Количество": "{} {}".format(
                                    product["quantity"], product["measureName"]
                                ),
                            }
                        )

            return result

        if session.params["inputs"]["0"]["report"] == "order_constructor":
            # Извлекаем параметры из запроса
            params = session["params"]["inputs"]["0"]
            counterparty = params["counterparty"]

            # Преобразуем даты в нужный формат
            since = get(params["openDate"]).replace(hour=3, minute=00).isoformat()
            until = get(params["closeDate"]).replace(hour=23, minute=00).isoformat()
            since1 = utcnow().replace(hour=3, minute=00).isoformat()
            until1 = utcnow().replace(hour=23, minute=00).isoformat()

            # Задаем набор магазинов для двух разных групп
            shops_uuid_2 = (
                "20190411-5A3A-40AC-80B3-8B405633C8BA",
                "20191117-BF71-40FE-8016-1E7E4A3A4780",
                "20231001-6611-407F-8068-AC44283C9196",
                "20190327-A48C-407F-801F-DA33CB4FBBE9",
            )

            # Задаем группы товаров для контрагентов
            groupName = {
                "mega_": (
                    "МЕГАПОЛИС -СИГАРИЛЛЫ",
                    "МЕГАПОЛИС -ЭНЕРГЕТИКИ",
                    "МЕГАПОЛИС-ITJ",
                    "МЕГАПОЛИС-JTI",
                    "МЕГАПОЛИС-АКСЕСУАРЫ",
                    "МЕГАПОЛИС-ФМ",
                ),
                "sns_": ("СНС", "СНС- СИГАРИЛЛЫ", "СНС-АКСЕССУАРЫ", "СНС-ЭНЕРГЕТИКИ"),
                "don_": ("ДОНСКОЙ ТАБАК АКСЕСУАРЫ", "ДОНСКОЙ-ТАБАК"),
                "fizzy_": ("FIZZY"),
            }

            groupName2 = {
                "mega_": (
                    "МЕГАПОЛИС-ITJ",
                    "МЕГАПОЛИС-JTI",
                    "МЕГАПОЛИС-ФМ",
                    "МЕГАПОЛИС АКСЕСУАРЫ",
                ),
                "sns_": ("СНС", "СНС АКСЕССУАРЫ"),
                "don_": ("ДОНСКОЙ-ТАБАК", "ДОНСКОЙ-ТАБАК-АКСЕСУАРЫ"),
                "fizzy_": ("ЭЛЕКТРО"),
            }

            # Выбираем группу товаров в зависимости от магазина
            if params["shop"] not in shops_uuid_2:
                counterparty_ = groupName[counterparty]
            else:
                counterparty_ = groupName2[counterparty]

            # Извлекаем информацию о магазине
            shop_id = params["shop"]
            shopName = Shop.objects(uuid__exact=shop_id).only("name").first().name

            # Формируем начальную часть результата
            result = [
                {
                    "Магазин:".upper(): shopName,
                    "Начало пириода:": since[0:10],
                    "Окончание пириода:": until[0:10],
                    "⬇️⬇️⬇️".upper(): "Продажи/Отаток/Заказ",
                }
            ]

            sold_today = {"продано".upper(): "сегодня".upper()}
            # Для каждой группы товаров собираем статистику
            for i in counterparty_:
                # Запрос для поиска групп в модели Products с определенными условиями
                group = Products.objects(
                    shop_id__exact=shop_id, group__exact=True, name__exact=i
                )
                groupName_ = [element.name for element in group][0]
                groupUuid = [element.uuid for element in group]

                products = Products.objects(
                    shop_id__exact=shop_id, group__exact=False, parentUuid=groupUuid[0]
                )
                products_uuid = [element.uuid for element in products]

                # Фильтруем документы по заданным критериям
                documents = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since, "$lt": until},
                        "shop_id": shop_id,
                        "x_type": "SELL",
                        "transactions.commodityUuid": {"$in": products_uuid},
                    }
                )

                documents1 = Documents.objects(
                    __raw__={
                        "closeDate": {"$gte": since1, "$lt": until1},
                        "shop_id": shop_id,
                        "x_type": "SELL",
                        "transactions.commodityUuid": {"$in": products_uuid},
                    }
                )

                _dict = gather_statistics_uuid(documents, products_uuid)

                # _dict1 = gather_statistics_uuid(documents1, products_uuid)

                # sold_p = gather_statistics_name(documents, products_uuid)
                # sold_p["продано".upper()] = "{} - {}".format(since[8:10], until[8:10])
                # result.append(sold_p)

                sold_today.update(gather_statistics_name(documents1, products_uuid))

                commodity_balances = get_commodity_balances_all(shop_id, products_uuid)
                # pprint(commodity_balances)
                _dict3 = {"Заказ:".upper(): groupName_}
                if len(_dict) > 0:
                    for product in products:
                        # if product["uuid"] in _dict1:
                        #     sales_d = _dict1[product["uuid"]]
                        # else:
                        #     sales_d = 0

                        product_quantity = commodity_balances[product["uuid"]]

                        if product["uuid"] in _dict:
                            product_quantity_seller = _dict[product["uuid"]]
                        else:
                            product_quantity_seller = 0

                        order = int(product_quantity_seller) - int(product_quantity)

                        if order < 0:
                            order = 0
                        else:
                            order = order

                        if order > 0:
                            _dict3[product["name"]] = "{}/{}/{}".format(
                                product_quantity_seller, product_quantity, order
                            )

                result.append(_dict3)
            result.append(sold_today)
            return result

        if session.params["inputs"]["0"]["report"] == "get_accept":
            shops = get_shops(session)
            shop_id = shops["shop_id"]

            number = params["number"]

            documents = Documents.objects(
                __raw__={
                    "number": int(number),
                    "shop_id": {"$in": shop_id},
                }
            )
            _dict = {}
            _sum = 0
            for element in documents:
                for trans in element["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        _sum += int(trans["sum"])
                        _dict.update(
                            {
                                trans["commodityName"]: "{}п./{}/{}".format(
                                    trans["quantity"],
                                    trans["resultPrice"],
                                    trans["sum"],
                                )
                            }
                        )
            _dict.update({"sum": _sum})

            return [_dict]

        if session.params["inputs"]["0"]["report"] == "get_product_not_for_sale":
            # Преобразование периода из параметров сессии в формат даты
            since = period_to_date(session.params["inputs"]["0"]["period"])
            until = utcnow().isoformat()

            # Получение информации о магазинах из сессии
            shops = get_shops(session)
            shop_id = shops["shop_id"]
            shop_name = shops["shop_name"]

            # Если параметр "group" равен "all", получаем все товары в магазине
            if params["group"] == "all":
                products = Products.objects(
                    __raw__={
                        "shop_id": shop_id[0],
                    }
                )

            else:
                # Иначе получаем товары, принадлежащие определенной группе
                products = Products.objects(
                    __raw__={"shop_id": shop_id[0], "parentUuid": params["group"]}
                )
            # Получаем идентификаторы всех товаров в текущей группе
            products_uuid = [element.uuid for element in products]

            commodity_balances = get_commodity_balances_p(shop_id, products_uuid)

            # Поиск документов в базе данных с условиями по времени, магазинам и типу транзакции
            start_time = time.time()
            print(
                f"Start функции2: {time.strftime('%H:%M:%S', time.localtime(start_time))} "
            )
            documents = Documents.objects(
                __raw__={
                    "closeDate": {"$gte": since, "$lt": until},
                    "shop_id": {"$in": shop_id},
                    "x_type": "SELL",
                }
            )

            sell_uuid = []
            for doc in documents:
                for trans in doc["transactions"]:
                    if trans["x_type"] == "REGISTER_POSITION":
                        if trans["commodityUuid"] not in sell_uuid:
                            sell_uuid.append(trans["commodityUuid"])
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Время выполнения функции2: {execution_time:.2f} секунд")

            data_result = {}
            for k, v in commodity_balances.items():
                # pprint(k)
                # Проверка, что остаток товара не равен 0
                if v > 0:
                    # Проверка, что товар не был продан ранее
                    if k not in sell_uuid:
                        # Получение информации о продукте из базы данных
                        prod = Products.objects(uuid=k, group__exact=False).first()
                        data_result[k] = {"col": v, "sum": v * prod.price}
            # Сортировка словаря по убыванию суммы продаж и преобразование в упорядоченный словарь
            data_result = dict(
                OrderedDict(sorted(data_result.items(), key=lambda t: -t[1]["sum"]))
            )

            # Форматирование результатов группировки продаж
            result = format_sell_groups(data_result, since, until)

            return result
