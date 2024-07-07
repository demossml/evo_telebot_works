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


def generate(session: Session):
    try:
        # Получение параметров из сессии
        params = session.params["inputs"]["0"]

        data = Сonsent.objects(user_id=int(params["user_id"])).first()

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
        doc.add_paragraph(f'Фамилия: {data["full_name"].split()[0]}')
        doc.add_paragraph(f'Имя: {data["full_name"].split()[1]}')
        doc.add_paragraph(f'Отчество: {data["full_name"].split()[2]}')
        doc.add_paragraph(f'Дата рождения: {data["dateOf_birth"]}')
        doc.add_paragraph(f'Гражданство: {data["citizenship"]}')
        doc.add_paragraph(
            f'Место рождения (село город край область республика): {data["place_of_birth"]}'
        )
        doc.add_paragraph(f'Адрес (место жительства): {data["residence_address"]}')
        doc.add_paragraph(f'Адрес (место прописки): {data["registration_address"]}')
        doc.add_paragraph(f'Домашний телефон: {data["home_phone"]}')
        doc.add_paragraph("Сотовый телефон: [Not provided]")
        doc.add_paragraph("Рабочий телефон: [Not provided]")

        # Блок паспортных данных
        add_block_title(doc, "Паспортные данные")
        doc.add_paragraph("Паспортные данные: [Not provided]")

        # Блок семейного положения
        add_block_title(doc, "Семейное положение")
        doc.add_paragraph(f'Семейное положение: {data["counterparty"]}')
        doc.add_paragraph("Дети (пол возраст): [Not provided]")

        # Блок сведений о близких родственниках
        add_block_title(doc, "Сведения о близких родственниках")
        for relative in data["relatives_information"]:
            add_sub_title(doc, f'Степень родства: {relative["close_relati"]}')
            doc.add_paragraph(f'Ф.И.О.: {relative["full_name"]}')
            doc.add_paragraph(f'Дата рождения: {relative["dateOf_birth"]}')
            doc.add_paragraph(
                f'Место работы: {relative.get("сompany", "[Not provided]")}'
            )
            doc.add_paragraph("Должность: [Not provided]")
            doc.add_paragraph("Телефон: [Not provided]")
            doc.add_paragraph("Адрес (место жительства): [Not provided]")

        # Блок образования
        add_block_title(doc, "Образование")
        for edu in data["education"]:
            add_sub_title(doc, "Образование:")
            doc.add_paragraph(f'Дата поступления: {edu["education_start_date"]}')
            doc.add_paragraph(f'Дата окончания: {edu["education_end_date"]}')
            doc.add_paragraph(
                f'Название учебного заведения: {edu["education_institution_name"]}'
            )
            doc.add_paragraph(f'Специальность: {edu["specialization"]}')

        # Блок дополнительного образования
        add_block_title(doc, "Дополнительное образование")
        # Если нет отдельного ключа для дополнительного образования, используем тот же, что и для основного образования
        for edu in data["education"]:
            add_sub_title(doc, "Дополнительное образование:")
            doc.add_paragraph(f'Дата поступления: {edu["education_start_date"]}')
            doc.add_paragraph(f'Дата окончания: {edu["education_end_date"]}')
            doc.add_paragraph(
                f'Название учебного заведения: {edu["education_institution_name"]}'
            )
            doc.add_paragraph(f'Специальность: {edu["specialization"]}')

        # Блок навыков и умений
        add_block_title(doc, "Навыки и умения")
        doc.add_paragraph('Навыки: {data.get("skills", "[Not provided]")}')
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
        for work in data["works_information"]:
            doc.add_paragraph(f'Дата начала: {work["work_start_date"]}')
            doc.add_paragraph(f'Дата окончания: {work["work_end_date"]}')
            doc.add_paragraph(f'Наименование организации: {work["company"]}')
            doc.add_paragraph(f'Должность: {work["position"]}')
            doc.add_paragraph("Адрес организации: [Not provided]")
            doc.add_paragraph(
                f'Причина увольнения (фактическая): {work["reason_forLeaving"]}'
            )

        # Блок дополнительной информации
        add_block_title(doc, "Дополнительная информация")
        doc.add_paragraph(f'Желаемый уровень заработной платы: {data["desiredSalary"]}')
        doc.add_paragraph(f'Преимущества Вашей кандидатуры: {data["advantages"]}')
        doc.add_paragraph(f'Ваши хобби: {data["hobbies"]}')
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
