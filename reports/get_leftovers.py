from bd.model import Session, Shop, Products, Documents
from arrow import utcnow, get
from pprint import pprint
from .util import period_to_date, get_intervals, remainder


name = "ОСТАТКИ ➡ "
desc = "ОСТАТКИ"
mime = 'text'


class ReportsInput:
    desc = "Выберите отчет"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            #
            {"id": 'get_leftovers_by_pieces',
             "name": "✅ В ШТ"},
            {"id": 'get_report',
             "name": "✅ Заказы".upper()}
        ]

        return output


class PeriodOpenDateInput:
    name = "Магазин"
    desc = "Выберите период"
    type = 'SELECT'

    def get_options(self, session: Session):
        output = [{
            'id': "day",
            'name': 'День'
        },
            {
                'id': "week",
                'name': 'Неделя'
            },
            {
                'id': "fortnight",
                'name': 'Две недели'
            },
            {
                'id': "month",
                'name': 'Месяц'
            },
            {
                'id': "two months",
                'name': 'Два месяца'
            }
        ]

        return output


class OpenDateInput:
    desc = "Выберите дату начало пириода "
    type = 'SELECT'

    def get_options(self, session: Session):
        output = []
        # pprint(session['params']['inputs']['period'])
        since = period_to_date(session['params']['inputs']['0']['period'])
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


class CloseDateInput:
    desc = "Выберите дату окончание пириода "
    type = 'SELECT'

    def get_options(self, session: Session):
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


def get_inputs(session: Session):
    if session.params["inputs"]['0']:
        if 'report' in session.params["inputs"]['0']:
            if session.params["inputs"]['0']['report'] == 'get_leftovers_by_rb':
                return {
                }
            if session.params["inputs"]['0']['report'] == 'get_leftovers_by_pieces':
                return {
                }
            if session.params["inputs"]['0']['report'] == 'get_report':
                return {
                    "period": PeriodOpenDateInput,
                    "openDate": OpenDateInput,
                    "closeDate": CloseDateInput
                }
        else:
            return {
                'report': ReportsInput
            }
    else:
        return {
            'report': ReportsInput
        }


def generate(session: Session):
    print('test')
    params = session.params["inputs"]['0']

    shops =  [
            '20220501-DDCF-409A-8022-486441F27458',
            # '20200630-3E0D-4061-80C1-F7897E112F00',
            "20220501-9ADF-402C-8012-FB88547F6222",
            '20220501-3254-40E5-809E-AC6BB204D373',
            '20230214-33E5-4085-80A3-28C177E34112',
            '20220501-4D25-40AD-80DA-77FAE02A007E',
            '20220601-4E97-40A5-801B-1A29127AFA8B',
            "20220430-A472-40B8-8077-2EE96318B7E7"
        ]
    # i = 'PAYBACK', 'ACCEPT'
    x_type = ['SELL', 'PAYBACK', 'ACCEPT']
    if params['report'] == 'get_leftovers_by_pieces':
        result = {}
        for sh in shops:
            shop = Shop.objects(uuid=sh).only('name').first()
            shop_name = shop['name']
            # pprint(shop_name)

            products = Products.objects(__raw__={
                'shop_id': sh,
                'group': False
            })
            # pprint(products)
            uuids = [i.uuid for i in products]
            # pprint(uuids)
            for uuid in uuids:
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
                                    if shop_name in result:
                                        result[shop_name] += trans['balanceQuantity']
                                        result[shop_name] -= trans['quantity']
                                    else:
                                        result[shop_name] = trans['balanceQuantity']
                                        result[shop_name] -= trans['quantity']
                                    if documents.x_type == 'PAYBACK':
                                        if shop_name in result:
                                            result[shop_name] += trans['balanceQuantity']
                                            result[shop_name] += trans['quantity']
                                        else:
                                            result[shop_name] = trans['balanceQuantity']
                                            result[shop_name] += trans['quantity']
                                    if documents.x_type == 'ACCEPT':
                                        if shop_name in result:
                                            result[shop_name] += trans['balanceQuantity']
                                        else:
                                            result[shop_name] = trans['balanceQuantity']
        return [result]
    if params['report'] == 'get_leftovers_by_rb':

        result = {}
        for sh in shops:
            shop = Shop.objects(uuid=sh).only('name').first()
            shop_name = shop['name']
            # pprint(shop_name)

            products = Products.objects(__raw__={
                'shop_id': sh,
                'group': False
            })
            # pprint(products)
            uuids = [i.uuid for i in products]
            pprint(uuids)
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
                                    if shop_name in result:
                                        result[shop_name] += trans['balanceQuantity'] * cost_price
                                        result[shop_name] -= trans['quantity'] * cost_price
                                    else:
                                        result[shop_name] = trans['balanceQuantity'] * cost_price
                                        result[shop_name] -= trans['quantity'] * cost_price
                                    if documents.x_type == 'PAYBACK':
                                        if shop_name in result:
                                            result[shop_name] += trans['balanceQuantity'] * cost_price
                                            result[shop_name] += trans['quantity'] * cost_price
                                        else:
                                            result[shop_name] = trans['balanceQuantity'] * cost_price
                                            result[shop_name] += trans['quantity'] * cost_price
                                    if documents.x_type == 'ACCEPT':
                                        if shop_name in result:
                                            result[shop_name] += trans['balanceQuantity'] * cost_price
                                        else:
                                            result[shop_name] = trans['balanceQuantity'] * cost_price

        return [result]
    if params['report'] == 'get_report':
        pprint('test2')
        params = session['params']['inputs']['0']
        since = get(params['openDate']).replace(hour=3, minute=00).isoformat()
        until = get(params['closeDate']).replace(hour=23, minute=00).isoformat()
        shops_uuid = [
            '20220501-DDCF-409A-8022-486441F27458',
            # '20200630-3E0D-4061-80C1-F7897E112F00',
            "20220501-9ADF-402C-8012-FB88547F6222",
            '20220501-3254-40E5-809E-AC6BB204D373',
            '20230214-33E5-4085-80A3-28C177E34112',
            '20220501-4D25-40AD-80DA-77FAE02A007E',
            '20220601-4E97-40A5-801B-1A29127AFA8B',
            "20220430-A472-40B8-8077-2EE96318B7E7"
        ]
        remainder_ = remainder(shops_uuid)
        pprint(remainder_)

        result = [
            {'Начало пириода:': since[0:10]},
            {'Окончание пириода:': until[0:10]},

        ]
        for shop_id in shops_uuid:
            remainder_shop = 0
            for item in remainder_[shop_id]:
                for k_, v_ in item.items():
                    remainder_shop += v_

            shop_name = Shop.objects(uuid__exact=shop_id).only('name').first().name
            result.append({
                'Магазин:': shop_name,
                'Остаток:': remainder_shop
            })
            # pprint(shop_name)
            documents = Documents.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': shop_id,
                'x_type': 'SELL',
            })
            # pprint(documents)
            _dict = {}

            for doc in documents:
                for trans in doc['transactions']:
                    # pprint(trans)
                    if trans['x_type'] == 'REGISTER_POSITION':
                        if trans['commodityUuid'] in _dict:
                            _dict[trans['commodityUuid']] += trans['quantity']
                        else:
                            _dict[trans['commodityUuid']] = trans['quantity']

            # pprint(_dict)
            _dict3 = {}

            if len(_dict) > 0:
                products = remainder_[shop_id]
                for prod in products:
                    for k, v in prod.items():
                        product_uuid = k
                        prod_name = Products.objects(uuid__exact=k, group__exact=False).only('name').first().name
                        product_quantity = v
                    if product_uuid in _dict:
                        product_quantity_seller = _dict[product_uuid]
                    else:
                        product_quantity_seller = 0

                    # pprint(product_quantity_seller)

                    if product_quantity_seller > 0:
                        order = int(product_quantity_seller) - int(product_quantity)
                        if order < 0:
                            order = 0
                        else:
                            order = order
                        # pprint(order)
                        _dict3[prod_name] = '{}/{}/{}'.format(
                            product_quantity_seller,
                            product_quantity,
                            order
                        )
                pprint(_dict3)

                result.append(_dict3)
            else:
                result.append({'Заказа': 'нет'})
        return result
