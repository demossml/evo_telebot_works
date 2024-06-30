class QuestionnaireInput:
    desc = "Выберите раздел анкеты"
    type = "SELECT"

    def get_options(self, session: Session):
        sections = [
            {
                "id": "personal_information",
                "name": "Личная информация",
                "sub_sections": [
                    {"id": "full_name", "name": "Фамилия Имя Отчество"},
                    {"id": "date_of_birth", "name": "Дата рождения"},
                    {"id": "citizenship", "name": "Гражданство"},
                    {"id": "place_of_birth", "name": "Место рождения"},
                ],
            },
            {
                "id": "contact_information",
                "name": "Контактная информация",
                "sub_sections": [
                    {"id": "residence_address", "name": "Адрес (место жительства)"},
                    {"id": "registration_address", "name": "Адрес (место прописки)"},
                    {"id": "home_phone", "name": "Домашний телефон"},
                    {"id": "mobile_phone", "name": "Сотовый телефон"},
                ],
            },
            {
                "id": "family_status",
                "name": "Семейное положение",
                "sub_sections": [
                    {"id": "marital_status", "name": "Семейное положение"},
                    {"id": "children", "name": "Дети (пол, возраст)"},
                ],
            },
            {
                "id": "relatives_information",
                "name": "Сведения о близких родственниках",
                "sub_sections": [
                    {"id": "relative_full_name", "name": "Ф.И.О."},
                    {"id": "relative_dob", "name": "Дата рождения"},
                    {"id": "relative_work", "name": "Место работы, должность"},
                    {"id": "relative_phone", "name": "Телефон"},
                    {"id": "relative_address", "name": "Адрес (место жительства)"},
                ],
            },
            {
                "id": "education",
                "name": "Образование",
                "sub_sections": [
                    {"id": "start_date", "name": "Дата поступления"},
                    {"id": "end_date", "name": "Дата окончания"},
                    {"id": "institution_name", "name": "Название учебного заведения"},
                    {
                        "id": "additional_education",
                        "name": "Дополнительное образование",
                    },
                ],
            },
            {
                "id": "skills",
                "name": "Навыки",
                "sub_sections": [
                    {"id": "computer_skills", "name": "Навыки владения компьютером"},
                    {"id": "language_skills", "name": "Знание иностранных языков"},
                ],
            },
            {
                "id": "references",
                "name": "Рекомендатели",
                "sub_sections": [
                    {
                        "id": "referee_details",
                        "name": "Должность, Ф.И.О. и контактный телефон",
                    }
                ],
            },
            {
                "id": "work_experience",
                "name": "Трудовая деятельность",
                "sub_sections": [
                    {"id": "employment_period", "name": "Дата начала и окончания"},
                    {"id": "company_name", "name": "Наименование организации"},
                    {"id": "position", "name": "Должность"},
                    {"id": "company_address", "name": "Адрес организации"},
                    {"id": "reason_for_leaving", "name": "Причина увольнения"},
                ],
            },
            {"id": "desired_salary", "name": "Желаемый уровень заработной платы"},
            {"id": "advantages", "name": "Преимущества Вашей кандидатуры"},
            {"id": "hobbies", "name": "Ваши хобби"},
            {
                "id": "additional_information",
                "name": "Какую информацию Вы хотели бы добавить о себе",
            },
        ]

        return sections
