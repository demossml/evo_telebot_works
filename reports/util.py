from bd.model import Shop, Products, Documents, Employees, Session, Plan
from arrow import utcnow, get
from typing import List, Tuple
from pprint import pprint


# Принимает словарь с данными о продукте

def format_sell_groups(_dict: dict) -> list[dict]:
    """
    :param _dict: словарь с данными о продукте
    :return: [
    {
        '1 Наименование:': str,
        '2 Остаток:': str,
        '3 Цена поставки:': str,
        '4 Цена продажи:': str,
        '5 Сумма(цена поставки):': str
    }
    ]
    """
    result = []
    for k, v in _dict.items():
        prod = Products.objects(uuid=k, group__exact=False).first()
        result.append(
            {
                '1 Наименование:': prod.name,
                '2 Остаток:': '{} {}.'.format(v['col'], prod.measureName),
                '3 Цена поставки: ': '{} ₱'.format(prod.costPrice),
                '4 Цена продажи:': '{} ₱'.format(prod.price),
                '5 Сумма(цена поставки):': '{} ₱'.format(v['sum'])

            }
        )

    return result


def get_products(session: Session, shop_id: str) -> object:
    """
    :param session:
    :param shop_id: uuid: str магазина
    :return: Данные по продуктам магазина
    """
    if session.employee.role == "CASHIER":
        return Products.objects(shop_id__exact=shop_id, group__exact=True, uuid__in=None)
    if session.employee.role == "ADMIN":
        return Products.objects(shop_id__exact=shop_id, group__exact=True)


def get_group(session: Session) -> dict:
    """
    :param session:
    :return: {uuid: name} группы
    """
    uuid = []
    for item in Employees.objects(lastName=str(session.user_id)):
        for store in item.stores:
            if store not in uuid:
                uuid.append(store)

    group = {}
    for element in uuid:
        for item in Products.objects(shop_id__exact=element, group__exact=True):
            if item["uuid"] not in group:
                group.update(
                    {
                        item["uuid"]: item["name"]
                    }
                )
    return group


def get_shops(session: Session) -> dict:
    """
    :param session:
    :return: {
                'shop_id': ['shop_id', ...],
                'shop_name': 'name'
            }
    """
    params = session.params["inputs"]['0']
    uuid = []
    for item in Employees.objects(lastName=str(session.user_id)):
        for store in item.stores:
            if store not in uuid:
                uuid.append(store)
    if 'shop' in params:
        if params['shop'] == 'all':
            return {
                'shop_id': [item["uuid"] for item in Shop.objects(uuid__in=uuid)],
                'shop_name': 'Все'.upper()
            }
        else:
            shop = Shop.objects(uuid__exact=params['shop']).only('name').first()
            return {
                'shop_id': [params['shop']],
                'shop_name': shop.name
            }

    else:
        return {
            'shop_id': [item["uuid"] for item in Shop.objects(uuid__in=uuid)],
            'shop_name': 'Все'.upper()
        }


def get_shops_user_id(session: Session) -> object:
    """
    :param session:
    :return: shops пользователя telegram bot
    """
    uuid = []
    for item in Employees.objects(lastName=str(session.user_id)):
        for store in item.stores:
            if store not in uuid:
                uuid.append(store)
    return Shop.objects(uuid__in=uuid)


def get_shops_in(session: Session, _in=[], id_=[]):
    uuid = []
    uuid_id = ['20220501-11CA-40E0-8031-49EADC90D1C4',
               '20220501-DDCF-409A-8022-486441F27458',
               '20220501-9ADF-402C-8012-FB88547F6222',
               '20220501-3254-40E5-809E-AC6BB204D373',
               '20220501-CB2E-4020-808C-E3FD3CB1A1D4',
               '20220501-4D25-40AD-80DA-77FAE02A007E',
               '20220430-A472-40B8-8077-2EE96318B7E7',
               '20220506-AE5B-40BA-805B-D8DDBD408F24']

    if len(id_) > 0:
        # pprint(1)
        users = [uuid_id]
    else:
        # pprint(2)
        users = [element.stores for element in Employees.objects(lastName=str(session.user_id))]

    # pprint(users)
    for i in users:
        for e in i:
            if e in _in:
                if e not in uuid:
                    # pprint(e)
                    uuid.append(e)
            if session.user_id == 490899906:
                for el in _in:
                    uuid.append(el)
    # pprint(uuid)
    return Shop.objects(uuid__in=uuid)


def period_to_date(period: str) -> utcnow:
    """
    :param period: day, week,  fortnight, month, two months,
    :return: utcnow - period
    """
    if period == "day":
        return utcnow().to('local').replace(hour=3, minute=00).isoformat()
    if period == "week":
        return utcnow().to('local').shift(days=-7).replace(hour=3, minute=00).isoformat()
    if period == "fortnight":
        return utcnow().to('local').shift(days=-14).replace(hour=3, minute=00).isoformat()
    if period == "month":
        return utcnow().to('local').shift(months=-1).replace(hour=3, minute=00).isoformat()
    if period == "two months":
        return utcnow().to('local').shift(months=-2).replace(hour=3, minute=00).isoformat()
    if period == "6 months":
        return utcnow().to('local').shift(months=-6).replace(hour=3, minute=00).isoformat()
    if period == "12 months":
        return utcnow().to('local').shift(months=-12).replace(hour=3, minute=00).isoformat()
    if period == "24 months":
        return utcnow().to('local').shift(months=-24).replace(hour=3, minute=00).isoformat()
    if period == "48 months":
        return utcnow().to('local').shift(months=-48).replace(hour=3, minute=00).isoformat()
    raise Exception("Period is not supported")


def period_to_date_2(period: str) -> utcnow:
    """
       :param period: day, week,  fortnight, month, two months,
       :return: utcnow + period
       """
    if period == "day":
        return utcnow().replace(hour=3, minute=00).isoformat()
    if period == "week":
        return utcnow().shift(days=7).replace(hour=3, minute=00).isoformat()
    if period == "fortnight":
        return utcnow().shift(days=14).replace(hour=3, minute=00).isoformat()
    if period == "month":
        return utcnow().shift(months=1).replace(hour=3, minute=00).isoformat()
    if period == "two months":
        return utcnow().shift(months=2).replace(hour=3, minute=00).isoformat()
    if period == "6 months":
        return utcnow().shift(months=6).replace(hour=3, minute=00).isoformat()
    if period == "12 months":
        return utcnow().shift(months=12).replace(hour=3, minute=00).isoformat()
    if period == "24 months":
        return utcnow().shift(months=24).replace(hour=3, minute=00).isoformat()
    if period == "48 months":
        return utcnow().shift(months=48).replace(hour=3, minute=00).isoformat()
    raise Exception("Period is not supported")


def get_intervals(
        min_date: str, max_date: str, unit: str, measure: float
) -> List[Tuple[str, str]]:
    """
    :param min_date: дата начала пириода
    :param max_date: дата окончания пириода
    :param unit: days, weeks,  fortnights, months
    :param measure: int шаг
    :return: List[Tuple[min_date, max_date]]
    """
    output = []
    while min_date < max_date:
        # записывет в перменную temp минимальную дату плюс (unit: measure)
        temp = get(min_date).shift(**{unit: measure}).isoformat()
        # записывает в output пару дат min_date и  меньшую дату min_date max_date или temp
        output.append((min_date, min(temp, max_date)))
        # меняет значение min_date на temp
        min_date = temp
    return output


def get_employees(session: Session) -> object:
    """
    :param session:
    :return: employees пользователя telegram bot
    """
    uuid = []
    users = [element.stores for element in Employees.objects(lastName=str(session.user_id))]
    for i in users:
        for e in i:
            uuid.append(e)

    return Employees.objects(stores__in=uuid)


def get_products_all(session: Session, shop_id: list):
    """
    :param shop_id: [shop_id, ...]
    :param session:
    :return: {'uuid': 'name'}
    """
    result = {}
    for item in Products.objects(shop_id__in=shop_id, group__exact=True):
        if item['uuid'] not in result:
            result[item['uuid']] = item['name']
    return result


def get_period(session: Session):
    """
    :param session:
    :return: {'since': str, 'until': str}
    """
    period_in = ["day", "week", "fortnight", "month"]
    if session.params["inputs"]['0']['period'] not in period_in:
        return {
            'since': get(session.params["inputs"]['0']['openDate']).replace(day=1).isoformat(),
            'until': get(session.params["inputs"]['0']['openDate']).ceil('month').isoformat()
        }
    if session.params["inputs"]['0']['period'] == 'day':
        return {
            'since': period_to_date(session.params["inputs"]['0']['period']),
            'until': utcnow().isoformat()
        }

    else:
        return {
            'since': get(session.params["inputs"]['0']['openDate']).replace(hour=3, minute=00).isoformat(),
            'until': get(session.params["inputs"]['0']['closeDate']).replace(hour=23, minute=00).isoformat()
        }


def get_period_day(session: Session):
    """
    :param session:
    :return: {'since': str, 'until': str}
    """
    if session.params["inputs"]['0']['period'] == 'day':
        return {
            'since': period_to_date(session.params["inputs"]['0']['period']),
            'until': get(period_to_date(session.params["inputs"]['0']['period'])).replace(hour=23,
                                                                                          minute=00).isoformat()
        }

    else:
        pprint(7777777)
        return {
            'since': get(session.params["inputs"]['0']['openDate']).replace(hour=0, minute=1).isoformat(),
            'until': get(session.params["inputs"]['0']['openDate']).replace(hour=23, minute=59).isoformat()
        }


def get_period_order(session: Session):
    """
    :param session:
    :return: {'since': str, 'until': str}
    """
    data = get(period_to_date(session.params["inputs"]['0']['period']))
    pprint(data)
    if session.params["inputs"]['0']['period'] == 'day':
        return {
            'since': get(period_to_date(session.params["inputs"]['0']['period'])).shift(days=-7).replace(hour=00,
                                                                                                         minute=1).isoformat(),
            'until': utcnow().shift(days=-7).replace(hour=23, minute=59).isoformat()
        }

    else:
        return {
            'since': get(session.params["inputs"]['0']['openDate']).shift(days=-7).replace(hour=0,
                                                                                           minute=1).isoformat(),
            'until': get(session.params["inputs"]['0']['openDate']).shift(days=-7).replace(hour=23,
                                                                                           minute=59).isoformat()
        }


def get_commodity_balances(session: Session) -> dict:
    _dict = {}

    params = session.params["inputs"]['0']

    x_type = ['SELL', 'PAYBACK', 'ACCEPT']

    shops = get_shops(session)
    shop_id = shops['shop_id']

    for shop_uuid in shop_id:
        if params['group'] == 'all':
            products = Products.objects(__raw__={
                'shop_id': shop_uuid,
            })
            group_name = 'Все'
        else:
            products = Products.objects(__raw__={
                'shop_id': shop_uuid,
                'parentUuid': params['group']
            })
            porod = Products.objects(uuid=params['group'], group__exact=True).first()
            group_name = porod.name
        products_uuid = [element.uuid for element in products]

        for uuid in products_uuid:
            documents = Documents.objects(
                __raw__={
                    "shop_id": shop_uuid,
                    "x_type": {'$in': x_type},
                    'transactions.commodityUuid': uuid
                }
            ).order_by("-closeDate").first()

            if documents is not None:

                for trans in documents["transactions"]:
                    if trans["x_type"] == 'REGISTER_POSITION':

                        if trans['commodityUuid'] == uuid:

                            if documents.x_type == 'SELL':
                                _dict[trans['commodityUuid']] = trans['balanceQuantity'] - trans['quantity']

                            if documents.x_type == 'PAYBACK':
                                _dict[trans['commodityUuid']] = trans['balanceQuantity'] + trans['quantity']

                            if documents.x_type == 'ACCEPT':
                                _dict[trans['commodityUuid']] = trans['balanceQuantity']

    return _dict


def generate_plan():
    group_id = ["78ddfd78-dc52-11e8-b970-ccb0da458b5a", "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
                "0627db0b-4e39-11ec-ab27-2cf05d04be1d"]

    _in = ['20190411-5A3A-40AC-80B3-8B405633C8BA',
           '20190327-A48C-407F-801F-DA33CB4FBBE9',
           '20191117-BF71-40FE-8016-1E7E4A3A4780',
           '20210712-1362-4012-8026-5A35685630B2',
           '20220222-6C28-4069-8006-082BE12BEB32',
           '20200630-3E0D-4061-80C1-F7897E112F00',
           '20210923-FB1F-4023-80F6-9ECB3F5A0FA8',
           '20220201-19C9-40B0-8082-DF8A9067705D',
           '20220201-8B00-40C2-8002-EF7E53ED1220',
           '20220201-A55A-40B8-8071-EC8733AFFA8E',
           '20220202-B042-4021-803D-09E15DADE8A4']
    uuid = ['20210712-1362-4012-8026-5A35685630B2',
            '20220222-6C28-4069-8006-082BE12BEB32',
            '20200630-3E0D-4061-80C1-F7897E112F00',
            '20210923-FB1F-4023-80F6-9ECB3F5A0FA8',
            '20220201-19C9-40B0-8082-DF8A9067705D',
            '20220201-8B00-40C2-8002-EF7E53ED1220',
            '20220201-A55A-40B8-8071-EC8733AFFA8E',
            '20220202-B042-4021-803D-09E15DADE8A4']

    shops = Shop.objects(__raw__={
        'uuid': {'$in': _in}
    })

    _dict = {}

    for shop in shops:
        if shop['uuid'] in uuid:
            period = [7, 14, 21, 28]
        else:
            period = [7, 14, 21, 28]
        for element in period:
            # pprint('{} {}'. format(shop['name'], element))
            # pprint(shop['uuid'])
            since = utcnow().shift(days=-element).replace(hour=3, minute=00).isoformat()
            # pprint(since)
            until = utcnow().shift(days=-element).replace(hour=21, minute=00).isoformat()
            # pprint(until)
            products = Products.objects(__raw__={
                'shop_id': shop['uuid'],
                'parentUuid': {'$in': group_id}
            })

            products_uuid = [element.uuid for element in products]
            # pprint(products_uuid)
            x_type = ['SELL', 'PAYBACK']
            documents = Documents.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': shop['uuid'],
                'x_type': {'$in': x_type},
                'transactions.commodityUuid': {'$in': products_uuid}
            })

            sum_sell = 0

            for doc in documents:
                for trans in doc['transactions']:
                    if trans['x_type'] == 'REGISTER_POSITION':
                        if trans['commodityUuid'] in products_uuid:
                            sum_sell += trans['sum']
            if shop['uuid'] in uuid:
                _day = 4
            else:
                _day = 4

            if shop['uuid'] in _dict:
                _dict[shop['uuid']] += round((int(sum_sell) / _day + int(sum_sell) / 5 / 100 * 4))
            else:
                _dict[shop['uuid']] = round((int(sum_sell) / _day + int(sum_sell) / 5 / 100 * 4))
    for k, v in _dict.items():
        params = {
            'closeDate': utcnow().isoformat(),
            'shop_id': k
        }

        if v < 2500:
            params['sum'] = int(2500)
        else:
            params['sum'] = v
        # print(params)
        Plan.objects(closeDate=utcnow().isoformat()).update(**params, upsert=True)
    return params


def remainder(shops_uuid: list):
    x_type = ['SELL', 'PAYBACK', 'ACCEPT']

    result = {}
    for sh in shops_uuid:
        result[sh] = []
        shop = Shop.objects(uuid=sh).only('name').first()

        products = Products.objects(__raw__={
            'shop_id': sh,
            'group': False
        })
        # pprint(products)
        uuids = [i.uuid for i in products]
        # pprint(uuids)
        for uuid in uuids:
            product = Products.objects(uuid=uuid).first()
            # pprint(product)
            cost_price = product['costPrice']
            # pprint(cost_price)
            documents = Documents.objects(
                __raw__={
                    "shop_id": sh,
                    "x_type": {'$in': x_type},
                    'transactions.commodityUuid': uuid
                }
            ).order_by("-closeDate").first()

            # pprint(documents)
            # pprint('e')
            if documents is not None:
                for trans in documents["transactions"]:
                    if trans["x_type"] == 'REGISTER_POSITION':
                        if trans['commodityUuid'] == uuid:
                            if documents.x_type == 'SELL':
                                if trans['balanceQuantity'] - trans['quantity'] > 0:
                                    result[sh].append(
                                        {trans['commodityUuid']: trans['balanceQuantity'] - trans['quantity']})
                            if documents.x_type == 'PAYBACK':
                                # pprint(trans)
                                if trans['balanceQuantity'] + trans['quantity'] > 0:
                                    result[sh].append(
                                        {trans['commodityUuid']: trans['balanceQuantity'] + trans['quantity']})
                            if documents.x_type == 'ACCEPT':
                                # pprint(documents.closeDate)
                                result[sh].append(
                                    {trans['commodityUuid']: trans['quantity']})
    return result
