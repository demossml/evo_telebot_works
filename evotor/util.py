# from tc.config import  EVOTOR_TOKEN_5, EVOTOR_TOKEN_2, EVOTOR_TOKEN_3, EVOTOR_TOKEN_4
from evotor import Evotor
from bd.model import Shop, Products, Documents, Employees
from pprint import pprint
from arrow import utcnow, get
from typing import List, Tuple


def prune(obj):
    """
    Функция для обработки словарей и списков, изменяя ключи "type" и "size" на "x_type" и "x_size".

    Args:
    obj (dict или list): Входной объект (словарь или список).

    Returns:
    obj (dict, list или None): Обработанный объект или None, если входной объект пустой.
    """
    # Проверяем, является ли объект словарем (dict)
    if isinstance(obj, dict):
        # Если словарь не пустой
        if len(obj) > 0:
            # Создаем новый пустой словарь для вывода
            out = {}
            for key, value in obj.items():
                # Если ключ равен "type" или "size", добавляем префикс "x_" к ключу
                if key == "type" or key == "size":
                    key = "x_" + key
                # Рекурсивно вызываем функцию prune для значения и добавляем его в новый словарь
                out[key] = prune(value)
            # Возвращаем новый словарь после обработки
            return out
        else:
            # Если словарь пустой, возвращаем None
            return None
    # Проверяем, является ли объект списком (list)
    elif isinstance(obj, list):
        # Если список не пустой
        if len(obj) > 0:
            # Перебираем элементы списка по индексам
            for index, value in enumerate(obj):
                # Рекурсивно вызываем функцию prune для элемента списка
                obj[index] = prune(value)
            # Возвращаем измененный список после обработки
            return obj
        else:
            # Если список пустой, возвращаем None
            return None
    else:
        # Если объект не является ни словарем, ни списком, возвращаем его без изменений
        return obj


def get_intervals(min_date: str, max_date: str, unit: str, measure: float):
    output = []
    while min_date < max_date:
        # записывет в перменную temp минимальную дату плюс (unit: measure)
        temp = get(min_date).shift(**{unit: measure}).isoformat()
        # записывает в output пару дат min_date и  меньшую дату min_date max_date или temp
        output.append((min_date, min(temp, max_date)))
        # меняет значение min_date на temp
        min_date = temp
    return output
