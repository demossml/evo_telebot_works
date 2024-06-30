from arrow import utcnow, get
from bd.model import Shop, AfsRequest, Employees, GetTime
from bot.util import format_message_list2
from pprint import pprint


# # Функция для отправки сообщений по расписанию
async def send_scheduled_message(bot):
    pprint(4)
    # await bot.send_message(user_id, message)
    users = Employees.objects(role="ADMIN")

    since = utcnow().replace(hour=2).isoformat()
    until = utcnow().isoformat()

    for user in users:
        result = {}
        for shop in Shop.objects(__raw__={"uuid": {"$in": user.stores}}):

            documents = GetTime.objects(
                __raw__={"openingData": {"$gte": since}, "shopUuid": shop["uuid"]}
            )
            pprint(documents)
            result[shop["name"]] = "ЕЩЕ НЕ ОТКРЫТА!!!"

            for doc in documents:
                pprint(doc["openingData"])
                user_id = str(doc.user_id)
                pprint(user_id)
                employees = [
                    element["name"]
                    for element in Employees.objects(lastName=user_id).only("name")
                ]
                if doc["openingData"]:
                    result[shop["name"]] = "{} {}".format(
                        employees[0], doc["openingData"][11:16]
                    )

        for message in format_message_list2(result):
            try:
                bot.send_message(user.lastName, message, parse_mode="MarkdownV2")
            except Exception as ex:
                pprint("Ошибка отправки сообщения {}".format(user.lastName))
