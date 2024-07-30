import sys
import logging
from bd.model import Сonsent


logger = logging.getLogger(__name__)


def generate_text_message(user_id: int):
    try:
        data = Сonsent.objects().first()

        if not data:
            raise ValueError("No data found for the given user_id.")

        not_provided = "[Not provided] ❌"
        message = ""

        # Функция для добавления заголовка блока
        def add_block_title(title, emoji):
            nonlocal message
            message += f"\n\n{emoji} **{title}**\n"

        # Функция для добавления подзаголовка
        def add_sub_title(title):
            nonlocal message
            message += f"\n{title}\n"

        # Заголовок анкеты
        message += "📝 **АНКЕТА**\n"

        # Заполнение документа данными из JSON

        # Блок личной информации
        add_block_title("Личная информация", "👤")
        full_name = data.full_name.split()
        message += (
            f"Фамилия: {full_name[0] if len(full_name) > 0 else not_provided}\n"
            f"Имя: {full_name[1] if len(full_name) > 1 else not_provided}\n"
            f"Отчество: {full_name[2] if len(full_name) > 2 else not_provided}\n"
            f'Дата рождения: {getattr(data, "dateOf_birth", not_provided)}\n'
            f'Гражданство: {getattr(data, "citizenship", not_provided)}\n'
            f'Место рождения (село город край область республика): {getattr(data, "place_of_birth", not_provided)}\n'
            f'Адрес (место жительства): {getattr(data, "residence_address", not_provided)}\n'
            f'Адрес (место прописки): {getattr(data, "registration_address", not_provided)}\n'
            f'Домашний телефон: {getattr(data, "home_phone", not_provided)}\n'
            f"Сотовый телефон: {not_provided}\n"
            f"Рабочий телефон: {not_provided}\n"
        )

        # Блок паспортных данных
        add_block_title("Паспортные данные", "🛂")
        message += f"Паспортные данные: {not_provided}\n"

        # Блок семейного положения
        add_block_title("Семейное положение", "👪")
        message += f'Семейное положение: {getattr(data, "counterparty", not_provided)}\nДети (пол возраст): {not_provided}\n'

        # Блок сведений о близких родственниках
        add_block_title("Сведения о близких родственниках", "👨‍👩‍👧‍👦")
        for relative in getattr(data, "relatives_information", []):
            add_sub_title(
                f'Степень родства: {relative.get("close_relati", not_provided)}'
            )
            message += (
                f'Ф.И.О.: {relative.get("full_name", not_provided)}\n'
                f'Дата рождения: {relative.get("dateOf_birth", not_provided)}\n'
                f'Место работы: {relative.get("сompany", not_provided)}\n'
                f"Должность: {not_provided}\n"
                f"Телефон: {not_provided}\n"
                f"Адрес (место жительства): {not_provided}\n"
            )

        # Блок образования
        add_block_title("Образование", "🎓")
        for edu in getattr(data, "education", []):
            add_sub_title("Образование:")
            message += (
                f'Дата поступления: {edu.get("education_start_date", not_provided)}\n'
                f'Дата окончания: {edu.get("education_end_date", not_provided)}\n'
                f'Название учебного заведения: {edu.get("education_institution_name", not_provided)}\n'
                f'Специальность: {edu.get("specialization", not_provided)}\n'
            )

        # Блок дополнительного образования
        add_block_title("Дополнительное образование", "📚")
        for edu in getattr(data, "education", []):
            add_sub_title("Дополнительное образование:")
            message += (
                f'Дата поступления: {edu.get("education_start_date", not_provided)}\n'
                f'Дата окончания: {edu.get("education_end_date", not_provided)}\n'
                f'Название учебного заведения: {edu.get("education_institution_name", not_provided)}\n'
                f'Специальность: {edu.get("specialization", not_provided)}\n'
            )

        # Блок навыков и умений
        add_block_title("Навыки и умения", "💼")
        message += f'Навыки: {getattr(data, "skills", not_provided)}\nЗнание иностранных языков степень владения: {not_provided}\n'

        # Блок трудовой деятельности
        add_block_title("Трудовая деятельность", "🏢")
        message += "Трудовая деятельность (укажите в обратном хронологическом порядке 5 последних мест Вашей работы):\n"
        for work in getattr(data, "works_information", []):
            message += (
                f'Дата начала: {work.get("work_start_date", not_provided)}\n'
                f'Дата окончания: {work.get("work_end_date", not_provided)}\n'
                f'Наименование организации: {work.get("company", not_provided)}\n'
                f'Должность: {work.get("position", not_provided)}\n'
                f"Адрес организации: {not_provided}\n"
                f'Причина увольнения (фактическая): {work.get("reason_forLeaving", not_provided)}\n'
            )

        # Блок дополнительной информации
        add_block_title("Дополнительная информация", "ℹ️")
        message += (
            f'Желаемый уровень заработной платы: {getattr(data, "desiredSalary", not_provided)}\n'
            f'Преимущества Вашей кандидатуры: {getattr(data, "advantages", not_provided)}\n'
            f'Ваши хобби: {getattr(data, "hobbies", not_provided)}\n'
            f"Какую информацию Вы хотели бы добавить о себе: {not_provided}\n"
        )

        return message
    except Exception as e:
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
        return None
