from bd.model import Сonsent, Session
from .util import create_document
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
mime = "docx"


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
        data = Сonsent.objects(user_id=int(params["user_id"])).first()

        if not data:
            raise ValueError("No data found for the given user_id.")

        # Функция для добавления заголовка блока
        def add_block_title(doc, title):
            title_paragraph = doc.add_heading(title, level=2)
            title_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Функция для добавления подзаголовка
        def add_sub_title(doc, title):
            sub_title_paragraph = doc.add_paragraph(title)
            sub_title_paragraph.style.font.bold = True

        # Создаем новый документ
        doc = Document()
        doc.add_heading("АНКЕТА", level=1)

        # Заполнение документа данными из JSON

        # Блок личной информации
        add_block_title(doc, "Личная информация")
        full_name = data.full_name.split()
        doc.add_paragraph(
            f'Фамилия: {full_name[0] if len(full_name) > 0 else "[Not provided]"}'
        )
        doc.add_paragraph(
            f'Имя: {full_name[1] if len(full_name) > 1 else "[Not provided]"}'
        )
        doc.add_paragraph(
            f'Отчество: {full_name[2] if len(full_name) > 2 else "[Not provided]"}'
        )
        doc.add_paragraph(
            f'Дата рождения: {getattr(data, "dateOf_birth", "[Not provided]")}'
        )
        doc.add_paragraph(
            f'Гражданство: {getattr(data, "citizenship", "[Not provided]")}'
        )
        doc.add_paragraph(
            f'Место рождения (село город край область республика): {getattr(data, "place_of_birth", "[Not provided]")}'
        )
        doc.add_paragraph(
            f'Адрес (место жительства): {getattr(data, "residence_address", "[Not provided]")}'
        )
        doc.add_paragraph(
            f'Адрес (место прописки): {getattr(data, "registration_address", "[Not provided]")}'
        )
        doc.add_paragraph(
            f'Домашний телефон: {getattr(data, "home_phone", "[Not provided]")}'
        )
        doc.add_paragraph("Сотовый телефон: [Not provided]")
        doc.add_paragraph("Рабочий телефон: [Not provided]")

        # Блок паспортных данных
        add_block_title(doc, "Паспортные данные")
        doc.add_paragraph("Паспортные данные: [Not provided]")

        # Блок семейного положения
        add_block_title(doc, "Семейное положение")
        doc.add_paragraph(
            f'Семейное положение: {getattr(data, "counterparty", "[Not provided]")}'
        )
        doc.add_paragraph("Дети (пол возраст): [Not provided]")

        # Блок сведений о близких родственниках
        add_block_title(doc, "Сведения о близких родственниках")
        for relative in getattr(data, "relatives_information", []):
            add_sub_title(
                doc,
                f'Степень родства: {relative.get("close_relati", "[Not provided]")}',
            )
            doc.add_paragraph(f'Ф.И.О.: {relative.get("full_name", "[Not provided]")}')
            doc.add_paragraph(
                f'Дата рождения: {relative.get("dateOf_birth", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Место работы: {relative.get("сompany", "[Not provided]")}'
            )
            doc.add_paragraph("Должность: [Not provided]")
            doc.add_paragraph("Телефон: [Not provided]")
            doc.add_paragraph("Адрес (место жительства): [Not provided]")

        # Блок образования
        add_block_title(doc, "Образование")
        for edu in getattr(data, "education", []):
            add_sub_title(doc, "Образование:")
            doc.add_paragraph(
                f'Дата поступления: {edu.get("education_start_date", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Дата окончания: {edu.get("education_end_date", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Название учебного заведения: {edu.get("education_institution_name", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Специальность: {edu.get("specialization", "[Not provided]")}'
            )

        # Блок дополнительного образования
        add_block_title(doc, "Дополнительное образование")
        # Если нет отдельного ключа для дополнительного образования, используем тот же, что и для основного образования
        for edu in getattr(data, "education", []):
            add_sub_title(doc, "Дополнительное образование:")
            doc.add_paragraph(
                f'Дата поступления: {edu.get("education_start_date", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Дата окончания: {edu.get("education_end_date", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Название учебного заведения: {edu.get("education_institution_name", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Специальность: {edu.get("specialization", "[Not provided]")}'
            )

        # Блок навыков и умений
        add_block_title(doc, "Навыки и умения")
        doc.add_paragraph(f'Навыки: {getattr(data, "skills", "[Not provided]")}')
        doc.add_paragraph("Знание иностранных языков степень владения: [Not provided]")

        # Блок рекомендателей
        add_block_title(doc, "Рекомендатели")
        doc.add_paragraph(
            "Рекомендатели (должность Ф.И.О. и контактный телефон): [Not provided]"
        )

        # Блок трудовой деятельности
        add_block_title(doc, "Трудовая деятельность")
        doc.add_paragraph(
            "Трудовая деятельность (укажите в обратном хронологическом порядке 5 последних мест Вашей работы):"
        )
        for work in getattr(data, "works_information", []):
            doc.add_paragraph(
                f'Дата начала: {work.get("work_start_date", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Дата окончания: {work.get("work_end_date", "[Not provided]")}'
            )
            doc.add_paragraph(
                f'Наименование организации: {work.get("company", "[Not provided]")}'
            )
            doc.add_paragraph(f'Должность: {work.get("position", "[Not provided]")}')
            doc.add_paragraph("Адрес организации: [Not provided]")
            doc.add_paragraph(
                f'Причина увольнения (фактическая): {work.get("reason_forLeaving", "[Not provided]")}'
            )

        # Блок дополнительной информации
        add_block_title(doc, "Дополнительная информация")
        doc.add_paragraph(
            f'Желаемый уровень заработной платы: {getattr(data, "desiredSalary", "[Not provided]")}'
        )
        doc.add_paragraph(
            f'Преимущества Вашей кандидатуры: {getattr(data, "advantages", "[Not provided]")}'
        )
        doc.add_paragraph(f'Ваши хобби: {getattr(data, "hobbies", "[Not provided]")}')
        doc.add_paragraph(
            "Какую информацию Вы хотели бы добавить о себе: [Not provided]"
        )

        # Блок согласия на проверку информации
        add_block_title(doc, "Согласие на проверку информации")
        doc.add_paragraph(
            "Против проверки предоставленной мною информации не возражаю."
        )

        # Блок даты и подписи
        add_block_title(doc, "Дата и подпись")
        doc.add_paragraph("Дата заполнения: [Not provided]")
        doc.add_paragraph("Подпись: [Not provided]")

        return doc
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
        return None
