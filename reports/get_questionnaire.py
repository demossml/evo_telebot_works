from bd.model import Сonsent, Session
from .util import generate_text_message
from pprint import pprint
from collections import OrderedDict


from .inputs import (
    QuestionnaireInput,
)
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from io import BytesIO

import sys
import logging

logger = logging.getLogger(__name__)

name = "📃 Анкеты ➡️"
desc = "Анкеты"
mime = "questionnaires"


def get_inputs(session: Session):

    return {
        "user_id": QuestionnaireInput,
    }


from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import sys


def generate(session: Session):
    try:
        # Получение параметров из сессии
        params = session.params["inputs"]["0"]

        return generate_text_message(params["user_id"])
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
        return None
