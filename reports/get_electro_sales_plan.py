# Получить план продажи по группе товаров по всем магазинам в руб.
# Параметры отчета:
# - shop_id, id магазина из списка (загрузить id магазина из базы tc)
# - group_id, id групы товаров из списка (загрузить группы товаров из базы tc)
# - period, название периода из списка (день, неделя,  две недели, месяц)

from bd.model import Session, Shop, Products, Documents, Employees, Message, Plan
from arrow import utcnow
from pprint import pprint
from .util import get_shops, get_shops_in, generate_plan
import telebot

name = "💹 План по Электронкам ➡️".upper()
desc = "Генерирует отчет по продажам в шт. по одной группе товаров в одном магазине за фиксированный период"
mime = 'text'


def get_inputs(session: Session):
    return {}


def generate(session: Session):
    # params = session.params["inputs"]
    group_id = ["78ddfd78-dc52-11e8-b970-ccb0da458b5a", "bc9e7e4c-fdac-11ea-aaf2-2cf05d04be1d",
                "0627db0b-4e39-11ec-ab27-2cf05d04be1d"]
    since_2 = utcnow().replace(hour=3, minute=00).isoformat()
    until_2 = utcnow().isoformat()

    _in = [
        '20190411-5A3A-40AC-80B3-8B405633C8BA',
        '20190327-A48C-407F-801F-DA33CB4FBBE9',
        '20191117-BF71-40FE-8016-1E7E4A3A4780',
        '20210712-1362-4012-8026-5A35685630B2',
        '20220222-6C28-4069-8006-082BE12BEB32',
        '20200630-3E0D-4061-80C1-F7897E112F00',
        '20210923-FB1F-4023-80F6-9ECB3F5A0FA8',
        '20220201-19C9-40B0-8082-DF8A9067705D',
        '20220201-8B00-40C2-8002-EF7E53ED1220',
        '20220201-A55A-40B8-8071-EC8733AFFA8E',
        '20220202-B042-4021-803D-09E15DADE8A4',
     ]
    uuid = ['20210712-1362-4012-8026-5A35685630B2',
            '20220222-6C28-4069-8006-082BE12BEB32',
            '20200630-3E0D-4061-80C1-F7897E112F00',
            '20210923-FB1F-4023-80F6-9ECB3F5A0FA8',
            '20220201-19C9-40B0-8082-DF8A9067705D',
            '20220201-8B00-40C2-8002-EF7E53ED1220',
            '20220201-A55A-40B8-8071-EC8733AFFA8E',
            '20220202-B042-4021-803D-09E15DADE8A4']

    shops = get_shops_in(session, _in)

    _dict = {}
    _dict_2 = {}

    for shop in shops:
        since = utcnow().replace(hour=3, minute=00).isoformat()
        until = utcnow().replace(hour=20, minute=59).isoformat()

        plan_ = Plan.objects(__raw__={
            'closeDate': {'$gte': since, '$lt': until},
            'shop_id': shop['uuid'],
        })
        if len(plan_) > 0:
            # pprint(1)
            plan = Plan.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': shop['uuid'],
            }).first()
        else:
            generate_plan()
            # pprint(2)
            plan = Plan.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': shop['uuid'],
            }).first()

        products = Products.objects(__raw__={
            'shop_id': shop['uuid'],
            'parentUuid': {'$in': group_id}
        })

        products_uuid = [element.uuid for element in products]
        x_type = ['SELL', 'PAYBACK']
        documents_2 = Documents.objects(__raw__={
            'closeDate': {'$gte': since_2, '$lt': until_2},
            'shop_id': shop['uuid'],
            'x_type': {'$in': x_type},
            'transactions.commodityUuid': {'$in': products_uuid}
        })
        sum_sell_today = 0
        for doc_2 in documents_2:
            for trans_2 in doc_2['transactions']:
                if trans_2['x_type'] == 'REGISTER_POSITION':
                    if trans_2['commodityUuid'] in products_uuid:
                        sum_sell_today += trans_2['sum']

        if int(sum_sell_today) >= int(plan.sum):
            symbol = '✅'
        else:
            symbol = '🔴'
        _dict_2['{}{}'.format(symbol, shop['name'][:9]).upper()] = "пл.{}₽/пр.{}₽".format(int(plan.sum),
                                                                                          int(sum_sell_today))

    return [_dict_2]
