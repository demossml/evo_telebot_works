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

    employee = [
        i.uuid
        for i in Employees.objects(lastName=str(session.user_id)).only("uuid").first()
    ]

    documents_open_session = Documents.objects(
        __raw__={
            "closeDate": {"$gte": since, "$lt": until},
            "openUserUuid": {"$in": employee},
            "x_type": "OPEN_SESSION",
        }
    ).first()

    documents_break = (
        Shift_Opening_Report.objects(
            __raw__={
                "openData": {"$gte": since, "$lt": until},
                "x_type": "BREAK",
                "break": "open",
                "shop_id": documents_open_session.shop_id,
            }
        )
        .order_by("-openData")
        .first()
    )
    if documents_break:
        break_data = {
            "user_id": session.user_id,
            "closeDate": params["location"]["data"],
            "openData": documents_break.openData,
            "break": "closed",
            "x_type": "BREAK",
            "shop_id": documents_open_session.shop_id,
            "close_location": params["location"],
        }
        result.append({"перерыв закончился".upper(): break_data["closeDate"][:16]})
    else:
        break_data = {
            "user_id": session.user_id,
            "openData": params["location"]["data"],
            "x_type": "BREAK",
            "break": "open",
            "shop_id": documents_open_session.shop_id,
            "open_location": params["location"],
        }
        result.append({"перерыв начался".upper(): break_data["openData"][:16]})

    Shift_Opening_Report.objects(
        user_id=session.user_id,
        openData=break_data["openData"],
    ).update(**break_data, upsert=True)

    return result
