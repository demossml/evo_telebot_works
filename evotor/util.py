# from tc.config import  EVOTOR_TOKEN_5, EVOTOR_TOKEN_2, EVOTOR_TOKEN_3, EVOTOR_TOKEN_4
from evotor import Evotor
from bd.model import Shop, Products, Documents, Employees
from pprint import pprint
from arrow import utcnow, get
from typing import List, Tuple


# Создает список интервалов дат с шагом 'measure'
# Принимает три аргумента минимальная дата, максимальная дата и интервал(шаг)
def prune(obj):
    if isinstance(obj, dict):
        if len(obj) > 0:
            out = {}
            for key, value in obj.items():
                if key == "type" or key == "size":
                    key = "x_" + key
                out[key] = prune(value)
            return out
        else:
            return None
    elif isinstance(obj, list):
        if len(obj) > 0:
            for index, value in enumerate(obj):
                obj[index] = prune(value)
            return obj
        else:
            return None
    else:
        return obj


def get_intervals(
        min_date: str, max_date: str, unit: str, measure: float
):
    output = []
    while min_date < max_date:
        # записывет в перменную temp минимальную дату плюс (unit: measure)
        temp = get(min_date).shift(**{unit: measure}).isoformat()
        # записывает в output пару дат min_date и  меньшую дату min_date max_date или temp
        output.append((min_date, min(temp, max_date)))
        # меняет значение min_date на temp
        min_date = temp
    return output


