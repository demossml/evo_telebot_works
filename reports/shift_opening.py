from arrow import utcnow, get
from bd.model import Session, Shift_Opening_Report, Plan, Employees, GetTime
from .util import generate_plan, get_shops, get_shops_user_id
from .inputs import ShopInput, OpenDatePast2Input, ReportsShiftOpeningInput, AfsInput

from pprint import pprint

name = "🕒 ⌛ 💰 📷Открытие ТТ ➡️".upper()
desc = "Собирает данные о открытии смены"
mime = 'image'


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


class Counting_MoneyInput:
    desc = "Напишите ок/сумма + или - (пересчет денег)✍️".upper()
    type = "MESSAGE"


def get_inputs(session: Session):
    if session.params["inputs"]['0']:
        if session.params["inputs"]['0']['report'] == 'shift_opening_report':
            if 'shop' in session.params["inputs"]['0']:
                if session.params["inputs"]['0']['shop'] == "20220222-6C28-4069-8006-082BE12BEB32":
                    return {
                        "location": AfsInput,
                        'cash_register_photo': CashRegisterPhotoInput,
                        'сabinets_photo': СabinetsPhotoInput,
                        'showcase_photo1': showcasePhoto1Input,
                        'showcase_photo2': showcasePhoto2Input,
                        'showcase_photo3': showcasePhoto3Input,
                        "photo_territory_1": PhotoTerritory1Input,
                        "photo_territory_2": PhotoTerritory2Input,
                        'counting_money': Counting_MoneyInput
                    }
                else:
                    return {
                        "shop": ShopInput,
                        "location": AfsInput,
                        'cash_register_photo': CashRegisterPhotoInput,
                        'сabinets_photo': СabinetsPhotoInput,
                        'showcase_photo1': showcasePhoto1Input,
                        'showcase_photo2': showcasePhoto2Input,
                        "photo_territory_1": PhotoTerritory1Input,
                        "photo_territory_2": PhotoTerritory2Input,
                        'counting_money': Counting_MoneyInput
                    }
            else:
                return {
                    "shop": ShopInput
                }
        if session.params["inputs"]['0']['report'] == 'get_shift_opening_report':
            if 'period' in session.params["inputs"]['0']:
                if session.params["inputs"]['0']['period'] == 'day':
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
        if session.params["inputs"]['0']['report'] == 'get_schedules':
            return {}

    else:
        return {
            'report': ReportsShiftOpeningInput,

        }


def generate(session: Session):
    _dict = {}
    _dict2 = {}
    if session.params["inputs"]['0']['report'] == 'shift_opening_report':
        session.params["inputs"]['0']['distribution_list'] = 'yes'
        session.params["inputs"]['0']['locationData'] = session.params["inputs"]['0']['location']['data']
        params = session.params["inputs"]['0']

        since = utcnow().replace(hour=3, minute=00).isoformat()
        until = utcnow().replace(hour=20, minute=59).isoformat()

        shop = params['shop']
        plan_today = Plan.objects(__raw__={
            'closeDate': {'$gte': since, '$lt': until},
            'shop_id': shop,
        }).first()
        if plan_today:
            plan = plan_today
        else:
            generate_plan()
            plan = Plan.objects(__raw__={
                'closeDate': {'$gte': since, '$lt': until},
                'shop_id': session.params["inputs"]['0'],
            }).first()
        Shift_Opening_Report.objects(
            user_id=session.user_id,
            locationData=session.params["inputs"]['0']['locationData']
        ).update(**params, upsert=True)
        _dict = {}
        _dict.update({'✅Смена открыта'.upper(): get(params['location']['data']).isoformat()[0:16],
                      'План по Fyzzi/Электро'.upper(): int(plan.sum)
                      })

        return {}, [_dict]

    if session.params["inputs"]['0']['report'] == 'get_shift_opening_report':
        params = session.params['inputs']['0']

        shops = get_shops(session)
        shop_id = shops['shop_id']
        shop_name = shops['shop_name']
        pprint(shop_id)
        _dict = {}
        documents = Shift_Opening_Report.objects(__raw__={
            # 'locationData': {'$gte': since, '$lt': until},
            'shop': {'$in': shop_id},
        }).order_by("-locationData").first()
        if documents:
            for i in documents:
                if 'photo' in i:
                    _dict[i] = documents[i]['photo']
                    print(_dict)
            employees = Employees.objects(lastName=str(documents['user_id'])).first()
            last_name = employees.lastName
            name_ = employees.name
            pprint(name_)
            # for i in Employees.objects(lastName=str(documents['user_id'])):
            _dict2 = {
                'Магазин:'.upper(): '{}:'.format(shop_name).upper(),
                'Сотрудник'.upper(): name_,
                'Время открытия TT'.upper(): documents['locationData'][0:16],
                'Касса'.upper(): documents['counting_money']
            }

            return _dict, [_dict2]
        else:
            return {}, [
                {
                    'Нет данных'.upper(): ''
                }
            ]

    if session.params["inputs"]['0']['report'] == 'get_schedules':
        shops = get_shops_user_id(session)

        since = utcnow().replace(hour=2).isoformat()
        _in = ['20210712-1362-4012-8026-5A35685630B2',
               '20220222-6C28-4069-8006-082BE12BEB32',
               '20200630-3E0D-4061-80C1-F7897E112F00',
               '20210923-FB1F-4023-80F6-9ECB3F5A0FA8',
               '20220201-19C9-40B0-8082-DF8A9067705D',
               '20220201-8B00-40C2-8002-EF7E53ED1220',
               '20220201-A55A-40B8-8071-EC8733AFFA8E',
               '20220202-B042-4021-803D-09E15DADE8A4',
               '20190411-5A3A-40AC-80B3-8B405633C8BA',
               '20190327-A48C-407F-801F-DA33CB4FBBE9',
               '20191117-BF71-40FE-8016-1E7E4A3A4780']
        result = {}

        for shop in shops:
            pprint(shop['name'])

            if shop["uuid"] in _in:
                pprint(shop["uuid"])
                documents = GetTime.objects(__raw__={
                    'openingData': {'$gte': since},
                    'shopUuid': shop["uuid"]
                }).first()
                pprint(documents)

                if documents:
                    # pprint(doc['openingData'])
                    user_id = str(documents.user_id)
                    # pprint(user_id)
                    employees = Employees.objects(lastName=str(user_id)).only('name').first()
                    pprint(employees.name)
                    if documents['openingData']:
                        result['{}'.format(shop['name'])] = '{} {}'.format(employees.name,
                                                                           documents['openingData'][11:16])
                else:
                    result.update({shop['name']: 'ЕЩЕ НЕ ОТКРЫТА!!!'.upper()})
            pprint(result)

        return {}, [result]
