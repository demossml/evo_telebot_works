from os import environ
from typing import Any, List, TypedDict
from arrow import utcnow
from dataclasses import dataclass
from telebot import types


from mongoengine import (
    DynamicDocument,
    FloatField,
    IntField,
    StringField,
    DictField,
    BinaryField,
    connect,
)
from dotenv import load_dotenv

load_dotenv()

from os import getenv


class Transaction(TypedDict):
    x_type: str
    uuid: str
    id: str
    userCode: str
    userUuid: str
    creationDate: str
    timezone: int
    baseDocumentNumber: str
    baseDocumentUUID: str
    clientName: str
    clientPhone: str
    couponNumber: str
    alcoholByVolume: int
    alcoholProductKindCode: int
    balanceQuantity: int
    barcode: str
    commodityCode: str
    commodityUuid: str
    commodityName: str
    commodityType: str
    costPrice: int
    fprintSection: str
    mark: str
    measureName: str
    tareVolume: int
    price: int
    quantity: int
    resultPrice: int
    resultSum: int
    sum: int
    positionId: str
    extraKeys: str
    resultTaxSum: int
    tax: str
    taxPercent: int
    taxRateCode: str
    taxSum: int
    paymentType: str


class Document(TypedDict):
    uuid: str
    closeDate: str
    closeResultSum: str
    closeSum: str
    closeUserCode: str
    closeUserUuid: str
    completeInventory: bool
    deviceId: str
    deviceUuid: str
    extras: str
    number: int
    openDate: str
    openUserCode: str
    openUserUuid: str
    sessionNumber: str
    sessionUUID: str
    shop_id: str
    storeUuid: str
    transactions: List[Transaction]
    version: str
    x_type: str


# Определение data-класса "Message" для хранения сообщений
@dataclass
class Message:
    user_id: int
    chat_id: int
    text: str
    is_callback: bool
    location: Any
    photo: None
    message_id: int
    document: None


def get_session_expiration():
    return utcnow().shift(hours=1).isoformat()


def get_answer_time():
    return utcnow().isoformat()


def get_session_params():
    return {}


# Описание класса Session, представляющего сессии пользователей
class Session(DynamicDocument):
    # ID пользователя из telegram
    # поле обязательно для заполнения
    # пример: 123456
    user_id = IntField(required=True)

    # время "срока годности" сессии
    # поле обязательно для заполнения
    # по умолчанию: 1 час с момента создания
    # пример: "2020-09-10T20:00:00.000Z"
    # expires_at = StringField(required=True, default=get_session_expiration)

    # состоятние сессии
    # поле обязательно для заполнения
    # пример: "START"
    state = StringField(required=True)

    # Параметры сесии ипользуются для сохронения данных о выборе пользовотелея
    params = DictField(required=False, default=get_session_params)

    employee: Any = None

    message: Message = None

    photo = BinaryField()  # Бинарное поле для хранения фото в виде байтов


class Shop(DynamicDocument):
    """
    Содержит данные магазинов
    """

    pass


class Users(DynamicDocument):
    """
    Содержит данные
    учетной записи эвотор, телеграм и эвотелебота
    """

    pass


class Documents(DynamicDocument):
    """Содержит данные документов"""

    pass


class Products(DynamicDocument):
    """Содержит данные продуктов"""

    pass


class Employees(DynamicDocument):
    """Содержит данные сотрудников"""

    pass


class Plan(DynamicDocument):
    pass


class Status(DynamicDocument):
    pass


class MonthlyResult(DynamicDocument):
    pass


class ZReopt(DynamicDocument):
    pass


class Shift_Opening_Report(DynamicDocument):
    """Содержит данные открытия магазинов"""

    pass


class MarriageWarehouse(DynamicDocument):
    pass


class Surplus(DynamicDocument):
    pass


class Schedules(DynamicDocument):
    pass


class Сonsent(DynamicDocument):
    pass


class GetTime(DynamicDocument):
    pass


class PromoUuid(DynamicDocument):
    """Содержит данные промо  продуктов"""

    pass


class GroupUuidAks(DynamicDocument):
    """
    Содержит данные груп аксесуаров
    """

    pass


class CashRegister(DynamicDocument):
    pass


class Chat(DynamicDocument):
    pass


class TimeSync(DynamicDocument):
    pass


class AfsRequest(DynamicDocument):
    # ID магазина
    # поле обязательно для заполнения
    # пример: 1
    shop_id = StringField(required=True)

    # ID пользователя из telegram
    # поле обязательно для заполнения
    # пример: 123456
    user_id = IntField(required=True)

    check_in_latitude = FloatField(required=True)
    check_in_longitude = FloatField(required=True)

    check_out_latitude = FloatField(required=False)
    check_out_longitude = FloatField(required=False)

    check_in = StringField(required=True, default=get_answer_time)
    check_out = StringField(required=False)


# Вспомогательные функции


# Функция для создания объекта "Message" на основе параметров
def create_massage(params):
    # Создание объекта "Message" на основе параметров сообщения
    if isinstance(params, types.Message):
        return Message(
            user_id=params.from_user.id,
            chat_id=params.chat.id,
            text=params.text,
            is_callback=False,
            location=params.location,
            photo=params.photo,
            message_id=params.message_id,
            document=params.document,
        )
    else:
        return Message(
            user_id=params.from_user.id,
            chat_id=params.message.chat.id,
            text=params.data,
            is_callback=True,
            location=None,
            photo=None,
            message_id=params.message.message_id,
            document=None,
        )


# Функция для получения сессии пользователя
def get_session(user_id):
    try:
        session = Session.objects(user_id=user_id)[0]
    except:
        session = Session(user_id=user_id, state="INIT", params={})

    session.save()

    return session


# Функция для поиска информации о сотруднике по ID пользователя
def find_employee(user_id):
    ids = [5700958253]
    if user_id in ids:
        return {}
    else:
        return Employees.objects(lastName__exact=str(user_id)).first()


# Инициирует подключение к базе данных mongodb
# http://docs.mongoengine.org/guide/connecting.html
#
connect(
    getenv("MONGODB_DATABASE"),
    username=getenv("MONGO_INITDB_ROOT_USERNAME"),
    password=getenv("MONGO_INITDB_ROOT_PASSWORD"),
    host=getenv("MONGODB_HOSTNAME"),
)
