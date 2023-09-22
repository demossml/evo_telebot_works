from arrow import utcnow, get
from bd.model import (
    Session,
    Shift_Opening_Report,
    Documents,
    Employees,
)
from .util import generate_plan, get_shops, get_shops_user_id
from .inputs import ShopInput, OpenDatePast2Input, AfsInput

from pprint import pprint

name = "🕒️🚬🌯перерыв ➡️".upper()
desc = "Собирает данные о перерывах"
mime = "text"


def get_inputs(session: Session):
    return {
        "location": AfsInput,
    }


def generate(session: Session):
    result = []

    params = session.params["inputs"]["0"]

    since = utcnow().replace(hour=3, minute=00).isoformat()
    until = utcnow().replace(hour=20, minute=59).isoformat()

    employee = [i.uuid for i in Employees.objects(lastName=str(session.user_id))]

    documents_open = (
        Shift_Opening_Report.objects(
            __raw__={
                "locationData": {"$gte": since, "$lt": until},
                "x_type": "OPEN",
                "user_id": session.user_id,
            }
        )
        .order_by("-openData")
        .first()
    )
    pprint(documents_open)
    documents_break = (
        Shift_Opening_Report.objects(
            __raw__={
                "openData": {"$gte": since, "$lt": until},
                "x_type": "BREAK",
                "break": "open",
                "shop_id": documents_open.shop,
            }
        )
        .order_by("-openData")
        .first()
    )
    if documents_break:
        delta = (
            (get(params["location"]["data"]) - get(documents_break.openData)).seconds
            // 60
            % 60
        )
        if delta > 0:
            result_delta = f"{delta} минут."
        else:
            result_delta = "Меньше минуты".upper()
        break_data = {
            "user_id": session.user_id,
            "closeDate": params["location"]["data"],
            "openData": documents_break.openData,
            "break": "closed",
            "x_type": "BREAK",
            "shop_id": documents_open.shop,
            "close_location": params["location"],
            "delta": delta,
        }

        result.append(
            {
                "перерыв закончился".upper(): break_data["closeDate"][:16],
                "Время перерыва:".upper(): result_delta,
            }
        )
    else:
        break_data = {
            "user_id": session.user_id,
            "openData": params["location"]["data"],
            "x_type": "BREAK",
            "break": "open",
            "shop_id": documents_open.shop,
            "open_location": params["location"],
        }
        result.append({"перерыв начался".upper(): break_data["openData"][:16]})

    Shift_Opening_Report.objects(
        user_id=session.user_id,
        openData=break_data["openData"],
    ).update(**break_data, upsert=True)

    return result
