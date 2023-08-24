from bd.model import Shop, Products, Documents, Session, Employees
from .util import get_intervals, \
    period_to_date, get_shops_user_id, get_group, get_period_day, period_to_date_2, get_period

from arrow import utcnow, get
from pprint import pprint


class ReportsMarriageInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": 'marriage_registration',
             "name": "Регистрация брака🚭⚠️➡️".upper()},
            {"id": 'get_marriage',
             "name": "Просмотреть брак нат ТТ🚭⚠️➡️".upper()},
        ]

        return output


class ReportsShiftOpeningInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        if session.employee.role == "CASHIER":
            output = [
                {"id": 'shift_opening_report',
                 "name": "Открытие ТТ ➡️".upper()},
            ]
        else:
            output = [
                {"id": 'shift_opening_report',
                 "name": "Открытие ТТ ➡️".upper()},
                {"id": 'get_shift_opening_report',
                 "name": "⌛ 💰 📷 ОТЧЕТЫ ОБ ОТКРЫТИИ ТТ ➡️ "},
                {"id": 'get_schedules',
                 "name": "Проверка время/чикина 🕒 ➡️".upper()},
            ]


        return output


class ReportsSurplusInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": 'register_surplus',
             "name": "Записать"},
            {"id": 'get_surplus',
             "name": "Просмотреть"},
        ]

        return output


class ReportsZReport2Input:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        if session.employee.role == "CASHIER":
            output = [
                {"id": 'z_report',
                 "name": "Заполнить Z Отчет 🧾".upper()},
                {"id": 'z_photo',
                 "name": "Загрузить фото 📷".upper()}

            ]
        else:
            output = [
                {"id": 'z_report',
                 "name": "Z Отчет 🧾".upper()},
                {"id": 'z_photo',
                 "name": "Загрузить фото 📷".upper()},
                {"id": 'get_z_report',
                 "name": "Просмотреть отчеты 👀".upper()}
            ]

        return output


class ReportsAcceptInput:
    """
    Приемка или Списание
    """
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        output = [
            {"id": 'get_accept',
             "name": "Приемка"},
            {"id": 'get_write_off',
             "name": "Списание"},
        ]

        return output


#
class ReportSalesInput:
    """
    Отчеты  по продажам
    """
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        output = [
            {"id": 'get_sales_by_day_of_the_week',
             "name": " 🛒📅 Продажи по дням нед... ➡️".upper()},
            {"id": 'get_sales_by_shop_product_group_unit',
             "name": "🛒 Продажи по товарам в шт  ➡️".upper()},
            {"id": 'get_sales_by_shop_product_group_rub',
             "name": "🛒 Продажи по товарам в ₽  ➡️".upper()},
            # {"id": 'get_sales_by_employees',
            #  "name": "🛒👱👱‍Продажи по продавцам ➡️".upper()},

        ]

        return output


class ReportsZInput:
    """
    Кассовые отчеты
    """
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        return [
            {"id": 'detailed_report',
             "name": '🧾 Z_Отчеты ➡️'.upper()},
            {"id": 'report_cash_outcome',
             "name": '🧾Отчет по выплатам ➡️'.upper()},
            {"id": 'report_cash_income',
             "name": '🧾Отчет по внесениям  ➡️'.upper()},
            {"id": 'get_check',
             "name": "🧾Запрос чека ➡️".upper()},
            {"id": 'surplus',
             "name": "🧾ИЗЛИШКИ В КАССЕ ➡️".upper()},
        ]


class ReportCommodityInput:
    """
    Tоварные отчеты
    """
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        output = [
            {"id": 'get_commodity_balances',
             "name": "™️ Товарные остатки  ➡️".upper()},
            {"id": 'order_constructor',
             "name": "🧮 Конструктор заказа  ➡️".upper()},
            {"id": 'get_accept',
             "name": "🚚 Приемка/Списание товара  ➡️".upper()},
            {"id": 'get_product_not_for_sale',
             "name": "🛑Товар без движиния(продаж) ➡️".upper()},
            {"id": 'marriage',
             "name": "Брак нат ТТ 🚭⚠️➡️".upper()},
        ]

        return output


class ShopAllInput:
    """
    Магазины и все магазины
    """
    desc = "Выберите магазин из списка"
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        output = [{"id": 'all', "name": '{} ➡️'.format('Все магазины').upper()}]

        for item in get_shops_user_id(session):
            output.append({"id": item["uuid"],
                           "name": '{} ➡️'.format(item["name"]).upper()
                           })

        return output


class ShopInput:
    """
    Магазины

    """
    desc = "Выберите магазин из списка"
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        output = []

        for item in get_shops_user_id(session):
            output.append({"id": item["uuid"],
                           "name": '{} ➡️'.format(item["name"]).upper()
                           })

        return output


class GroupInput:
    """
    Группы продуктов
    """
    name = "Группа товаров"
    desc = "Выберите группу товаров из списка 📋".upper()
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        output = [{"id": 'all', "name": '{} ➡️'.format('Все группы').upper()}]

        for k, v in get_group(session).items():
            output.append({
                "id": k,
                "name": '{} ➡️'.format(v)
            })

        return output


class ProductsInput:
    """
    Продукты
    """
    name = "Магазин"
    desc = "Выберите продукт"
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:
        output = []

        shop_id = [item["uuid"] for item in get_shops_user_id(session)]

        parentUuid = session.params["inputs"]['0']['Uuid']

        products = Products.objects(
            __raw__={
                'shop_id': {'$in': shop_id},
                # 'group': True,
                'parentUuid': parentUuid
            })

        for item in products:
            s = str(item['name']).split(' ')

            output.append({
                'id': item['uuid'],
                'name': ' '.join(s[0:4]),
                # 'name': item['name']
            })
        return output


class ProductElectroInput:
    name = "Выберите товар из списка"
    desc = "Выберите товар из списка™️➡️".upper()
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        shops_id = session.params["inputs"]['0']['shop']
        # pprint(shops_id)
        group_id = ["78ddfd78-dc52-11e8-b970-ccb0da458b5a", "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
                    "0627db0b-4e39-11ec-ab27-2cf05d04be1d"]
        product = Products.objects(__raw__={
            'shop_id': shops_id,
            'parentUuid': {'$in': group_id}
        })
        for item in product:
            # pprint(item['quantity'])
            # pprint(item['uuid'])
            # pprint(item['name'])
            if item['quantity']:
                s = str(item['name']).split(' ')

                # pprint(s)
                # pprint(' '.join(s[1:4]))
                output.append({
                    'id': item['uuid'],
                    'name': ' '.join(s[0:4])
                })

        return output


class ProductsSaleInput:
    """
    Продукты проданные за период
    """
    name = "Магазин"
    desc = "Выберите продукт".upper()
    type = "SELECT"

    def get_options(self, session: Session) -> [{str, str}]:

        output = []

        shops = get_shops_user_id(session)
        shop_id = shops['shop_id']

        parentUuid = session.params["inputs"]['0']['group']

        period = get_period_day(session)

        since = period['since']
        until = period['until']

        if parentUuid == 'all':
            products = Products.objects(__raw__={
                'shop_id': {'$in': shop_id},
            })
        else:
            products = Products.objects(__raw__={
                'shop_id': {'$in': shop_id},
                'parentUuid': parentUuid
            })
        products_uuid = [element.uuid for element in products]

        documents = Documents.objects(
            __raw__={
                "closeDate": {"$gte": since, "$lt": until},
                "shop_id": {'$in': shop_id},
                "x_type": "SELL",
                'transactions.commodityUuid': {'$in': products_uuid}
            })
        uuid_ = []
        _dict = {}
        for doc in documents:
            for trans in doc['transactions']:
                # pprint(trans)
                if trans['x_type'] == 'REGISTER_POSITION':

                    if trans['commodityUuid'] not in uuid_:
                        uuid_.append(trans['commodityUuid'])
                    if trans['commodityUuid'] not in _dict:
                        _dict[trans['commodityUuid']] = trans['quantity']
                    else:
                        _dict[trans['commodityUuid']] += trans['quantity']
        session.params['uuid'] = uuid_
        session.params['uuid_quantity'] = _dict

        uuid = []
        # содоет ключи в session.params["inputs"]
        for i in range(int(session['room']) + 1):
            # если в 'uuid' есть в session.params["inputs"][str(i)]
            if 'uuid' in session.params["inputs"][str(i)]:
                # если 'uuid' нет в словаре с ключем i в списке uuid
                if session.params["inputs"][str(i)]['uuid'] not in uuid:
                    # добовляет 'uuid' в список uuid
                    uuid.append(session.params["inputs"][str(i)]['uuid'])
        # Вытаскивает из бд session рание вабранны 'parentUuid' группы
        products = Products.objects(
            __raw__={
                'shop_id': {'$in': shop_id},
                # "group": True,
                'parentUuid': parentUuid,
                'uuid': {'$in': uuid_}
            })
        for item in products:
            # Если item['uuid'] нет в списке uuid
            if item['uuid'] not in uuid:
                # записывкет в output {'id': item['uuid'], 'name': item['name']}
                s = str(item['name']).split(' ')

                # pprint(s)
                # pprint(' '.join(s[1:4]))
                output.append({
                    'id': item['uuid'],
                    'name': ' '.join(s[1:4])
                })
        return output


class PeriodDateInput:
    """
    Предыдущие периоды
    """

    name = "Выберите период 📅".upper()
    desc = "Выберите период 📅".upper()
    type = 'SELECT'

    def get_options(self, session: Session) -> [{str, str}]:
        output = [{
            'id': "day",
            'name': '📆 День ➡️'.upper()
        },
            {
                'id': "week",
                'name': '📆 Неделя ➡️'.upper()
            },
            {
                'id': "fortnight",
                'name': '📆 Две недели ➡️'.upper()
            },
            {
                'id': "month",
                'name': '📆 Месяц ➡️'.upper()
            },
            {
                'id': "two months",
                'name': '📆 Два месяца ➡️'.upper()
            },
            {
                'id': "6 months",
                'name': '📆 6 Месяцев ➡️'.upper()
            },
            {
                'id': "12 months",
                'name': '📆 12 Месяцев ➡️'.upper()
            },
            {
                'id': "24 months",
                'name': '📆 24 Месяцев ➡️'.upper()
            },
            {
                'id': "48 months",
                'name': '📆 48 Месяцев ➡️'.upper()
            }

        ]

        return output


class OpenDatePastInput:
    """ Дата начала периода.
    Если период больше месяца даты будут месяцами.
    Иначе днями.
    От начала даты пириода до сегодняшней даты.
    """
    desc = "Выберите дату начало пириода "
    type = 'SELECT'

    def get_options(self, session: Session) -> [{str, str}]:
        output = []
        since = period_to_date(session['params']['inputs']['0']['period'])
        until = utcnow().isoformat()
        period = ["day", "week", "fortnight", "month"]
        if session['params']['inputs']['0']['period'] in period:
            intervals = get_intervals(since, until, "days", 1)
        else:
            intervals = get_intervals(since, until, "months", 1)
        for left, right in intervals:
            output.append({
                "id": left,
                "name": '{} ➡️'.format(left[0:10])
            })

        return output


class OpenDatePast2Input:
    """
    Дата начала пириода по дням.
    От начала даты пириода до сегодняшней даты.
    """
    desc = "Выберите дату начало пириода "
    type = 'SELECT'

    def get_options(self, session: Session) -> [{str, str}]:
        output = []
        since = period_to_date(session['params']['inputs']['0']['period'])
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)
        for left, right in intervals:
            output.append({
                "id": left,
                "name": '{} ➡️'.format(left[0:10])
            })

        return output


class OpenDateFutureInput:
    """
    Дата начала пириода по дням.
    От сегодняшней даты до конца даты пириода.
    """
    desc = "Выберите дату начало пириода "
    type = 'SELECT'

    def get_options(self, session: Session) -> [{str, str}]:
        output = []
        since = utcnow().isoformat()
        until = period_to_date_2(session['params']['inputs']['0']['period'])
        intervals = get_intervals(since, until, "days", 1)
        for left, right in intervals:
            output.append({
                "id": left,
                "name": '{} ➡️'.format(left[0:10])
            })

        return output


class CloseDatePastInput:
    """
    Дата окончания пириода по дням.
    От даты начала пириода до сегодняшней даты.
    """
    desc = "Выберите дату окончание пириода "
    type = 'SELECT'

    def get_options(self, session: Session) -> [{str, str}]:
        output = []
        # pprint(session['params']['inputs']['period'])
        since = session['params']['inputs']['0']['openDate']
        until = utcnow().isoformat()
        intervals = get_intervals(since, until, "days", 1)

        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({
                "id": left,
                "name": '{} ➡️'.format(left[0:10])
            })

        return output


class CloseDateFutureInput:
    """
    Дата окончания пириода по дням.
    От сегодняшней даты до даты начала пириода.
    """
    desc = "Выберите дату окончание пириода "
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = session['params']['inputs']['0']['openDate']
        until = period_to_date_2(session['params']['inputs']['0']['period'])
        intervals = get_intervals(since, until, "days", 1)

        # pprint(intervals)
        for left, right in intervals:
            # pprint(left)
            output.append({
                "id": left,
                "name": '{} ➡️'.format(left[0:10])
            })

        return output


class TokenEvotorInput:
    """
    Token Telebot
    """
    desc = "Напишите токен Telebot ✍️"
    type = "MESSAGE"


class DocumentsAcceptInput:
    """
    Выбор даты документа списания или приемки продукта
    """
    desc = "Выберите дату документа"
    type = 'SELECT'

    def get_options(self, session: Session) -> [{str, str}]:
        output = []
        params = session.params["inputs"]['0']
        period = get_period(session)

        since = period['since']
        until = period['until']

        shops = get_shops_user_id(session)
        shop_id = shops['shop_id']

        if params['report'] == 'get_accept':
            documents = Documents.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': {'$in': shop_id},
                'x_type': 'ACCEPT',
            })
        if params['report'] == 'get_write_off':
            documents = Documents.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': shop_id,
                'x_type': 'WRITE_OFF',
            })
            # pprint(documents)
        for item in documents:
            output.append({
                "id": item['number'],
                "name": get(item['closeDate']).shift(hours=3).isoformat()[0:10]
            })

        return output


class СounterpartyInput:
    name = "Группа товаров"
    desc = "Выберите контрагента товаров из списка"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {
                "id": 'sns_',
                "name": 'СНС'
            },
            {
                "id": 'don_',
                "name": 'ДОНСКОЙ-ТАБАК'
            },
            {
                "id": 'mega_',
                "name": 'МЕГАПОЛИС'
            },
            {
                "id": 'fizzy_',
                "name": 'FIZZY'
            },
        ]

        return output


class AfsInput:
    name = "Подтверждение".upper()
    desc = "Подтвердите 🗺".upper()
    type = "LOCATION"

    def get_options(self, session: Session):
        output = [{"name": "чекин"}]

        return output
