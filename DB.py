import random
import sqlite3
from fuzzywuzzy import fuzz, process

con = sqlite3.connect('DB.db')
cursor = con.cursor()

with con:
        # -- Создание таблицы "Пользователи"
        cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            user_tg_id INT NOT NULL
                          )''')

        # -- Создание таблицы "Ответы"
        cursor.execute('''CREATE TABLE IF NOT EXISTS Answer (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            answer TEXT
                            )''')

        # -- Создание таблицы "Инструкции"
        cursor.execute('''CREATE TABLE IF NOT EXISTS Instruction (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title VARCHAR(255) NOT NULL,
                            content TEXT NOT NULL,
                            count_click INT,
                            program_id INT,
                            rating FLOAT,
                            FOREIGN KEY (program_id) REFERENCES Program(id)
                        )''')

        # -- Создание таблицы "Пожелания пользователей"
        cursor.execute('''CREATE TABLE IF NOT EXISTS UserSuggestions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INT NOT NULL,
                            instruction_id INT NOT NULL,
                            suggestion TEXT,
                            status VARCHAR(100),
                            FOREIGN KEY (user_id) REFERENCES Users(id),
                            FOREIGN KEY (instruction_id) REFERENCES Instructions(id),
                            UNIQUE (user_id, instruction_id)
                        )''')

        # -- Создание таблицы "История изменений настроек бота"
        cursor.execute('''CREATE TABLE IF NOT EXISTS BotSettingsHistory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                            change_description TEXT
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS SettingsParagraph (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            paragraphs TEXT,
                            image TEXT,
                            page INT,
                            program_id INT,
                            FOREIGN KEY (program_id) REFERENCES Program(id)
                        )''')


        cursor.execute('''CREATE TABLE IF NOT EXISTS InstallationParagraph (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            paragraphs TEXT,
                            image TEXT,
                            page INT,
                            program_id INT,
                            FOREIGN KEY (program_id) REFERENCES Program(id)
                       )''')

        # -- Таблица установки и настроек программы
        cursor.execute('''CREATE TABLE IF NOT EXISTS Program (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            program_name VARCHAR(255)
                        )''')

        # -- Таблица операторов
        cursor.execute('''CREATE TABLE IF NOT EXISTS Operators (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            operator_name VARCHAR(50),
                            status BOOLEAN,
                            operators_tg_id INT
                        )''')

        # -- Таблица запросов пользователей
        cursor.execute('''CREATE TABLE IF NOT EXISTS UserQueries (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_tg_id INT,
                            query_text TEXT,
                            query_date DATETIME
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level INT,
                        login INT,
                        password INT
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS UserRatings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INT NOT NULL,
                        instruction_id INT NOT NULL,
                        rating FLOAT,
                        FOREIGN KEY (user_id) REFERENCES User(id),
                        FOREIGN KEY (instruction_id) REFERENCES Instruction(id),
                        UNIQUE (user_id, instruction_id)
                         );''')

class MethodsDB:
        def __init__(self, con: sqlite3.Connection):
                self.con = con
                self.cursor = con.cursor()

        def insert_user(self, username: str, user_tg_id: int):
                """
                Сбор данных пользователя (имя, id)
                :param username: имя пользователя
                :param user_id: id пользователя
                """
                # Проверяем, существует ли пользователь с таким user_id
                self.cursor.execute("SELECT COUNT(*) FROM User WHERE user_tg_id = ?", (user_tg_id,))
                count = self.cursor.fetchone()[0]

                if count == 0:
                        self.cursor.execute("INSERT INTO User (username, user_tg_id) VALUES (?, ?)", (username, user_tg_id))
                        self.con.commit()

        def get_answer(self, question: str):
                """
                Поиск похожего вопроса и получение на него ответа
                :param question: Сообщение от пользователя
                :return: Ответ из бд (Если ответа в базе нет, пустая строка)
                """
                # Получаем список всех вопросов из базы данных
                all_questions = [row[0] for row in self.cursor.execute('SELECT question FROM Answer').fetchall()]

                # Используем fuzzywuzzy для поиска наиболее похожего вопроса в списке
                closest_match = process.extractOne(question, all_questions)

                if closest_match is not None and closest_match[1] >= 60:
                        # Если совпадение было найдено, получаем ответ по этому вопросу
                        answer = self.cursor.execute('SELECT answer FROM Answer WHERE question = ?',
                                                     (closest_match[0],)).fetchone()

                        return answer[0] if answer else ""  # Возвращаем ответ или пустую строку, если ответ не найден
                else:
                        # Если достаточно похожего вопроса не найдено, возвращаем пустую строку
                        return "Извините, на данный вопрос у меня нет ответа😔, однако вы можете задать его оператору😇"

        def get_programs(self):
                """
                :return: Возвращает все имеющиеся программы в виде словаря, где id - ключ, название программы - значение
                """
                all_programs = self.cursor.execute('SELECT id, program_name FROM Program').fetchall()
                # Создаем словарь для хранения программ
                programs_dict = {}
                # Проходимся по каждой программе в результатах запроса
                for program in all_programs:
                        program_id, program_name = program
                        # Добавляем программу в словарь, где ключ - id, значение - название программы
                        programs_dict[program_id] = program_name
                return programs_dict

        def get_settings_paragraph(self, program_id: int):
                """
                :param program: на вход подается id программы
                :return: Выдает пункты установки программы
                """
                paragraphs = self.cursor.execute('SELECT paragraphs, page, image FROM Program '
                                                 'INNER JOIN SettingsParagraph '
                                                 'ON Program.id = SettingsParagraph.program_id '
                                                 'WHERE Program.id = ?', (program_id,)).fetchall()
                return paragraphs

        def get_install_paragraph(self, program_id: int):
                """
                :param program: на вход подается id программы
                :return: Выдается информация об установки программы
                """
                paragraphs = self.cursor.execute('SELECT paragraphs, page, image FROM Program '
                                                 'INNER JOIN InstallationParagraph '
                                                 'ON Program.id = InstallationParagraph.program_id '
                                                 'WHERE Program.id = ?', (program_id,)).fetchall()
                return paragraphs

        def get_instructions(self, program_id: int):
                """
                :param program_id: Айди программы
                :return: Выдает все инструкции с айдишкой
                """

                instructions = self.cursor.execute('SELECT Instruction.id, title, content FROM Instruction '
                                                   'INNER JOIN Program '
                                                   'ON Instruction.program_id = Program.id '
                                                   'WHERE Program.id = ?', (program_id,)).fetchall()
                return instructions

        def get_content(self, instruction_id: int):
                """
                :param instruction_id: Айди инструкции
                :return: Выыдает список кортежей
                """

                content = self.cursor.execute('SELECT  content FROM Instruction '
                                                   'WHERE id = ?', (instruction_id,)).fetchall()

                return content

        def get_free_operators(self):
                """
                :return: Получаем id свободного оператора
                """

                operators = self.cursor.execute('SELECT operator_name FROM Operators WHERE status = 0').fetchall()

                # Если список операторов не пустой, выбираем случайного оператора
                if operators:
                        random_operator = random.choice(operators)
                        return random_operator[0]
                else:
                        return None

        def get_all_operators(self):
                """
                :return: Получаем всех операторов
                """

                all_operators = self.cursor.execute('SELECT operators_tg_id FROM Operators').fetchall()

                return all_operators

        def enter_rating(self, user_tg_id: int, instruction_id: int, user_rating: int):
                """
                Обновление рейтинга в базе данных
                :param user_tg_id: ID пользователя
                :param instruction_id: ID инструкции
                :param user_rating: Оценка пользователя
                """
                try:
                        # Проверяем, существует ли запись в таблице User для указанного user_tg_id
                        user_id_row = self.cursor.execute('SELECT id FROM User WHERE user_tg_id = ?', (user_tg_id,))
                        user_id_result = user_id_row.fetchone()

                        # Если запись не существует, создаем новую запись для user_tg_id в таблице User
                        if user_id_result is None:
                                self.cursor.execute('INSERT INTO User (user_tg_id) VALUES (?)', (user_tg_id,))
                                self.con.commit()  # Не забываем фиксировать изменения
                                # Повторно выполняем запрос, чтобы получить user_id только что созданной записи
                                user_id_row = self.cursor.execute('SELECT id FROM User WHERE user_tg_id = ?',
                                                                  (user_tg_id,))
                                user_id_result = user_id_row.fetchone()

                        user_id = user_id_result[0]

                        existing_rating_row = self.cursor.execute(
                                'SELECT id FROM UserRatings WHERE user_id = ? AND instruction_id = ?',
                                (user_id, instruction_id))
                        existing_rating_result = existing_rating_row.fetchone()

                        if existing_rating_result is not None:

                                self.cursor.execute(
                                        "UPDATE UserRatings SET rating = ? WHERE user_id = ? AND instruction_id = ?",
                                        (user_rating, user_id, instruction_id))
                                self.con.commit()
                        else:

                                self.cursor.execute(
                                        "INSERT INTO UserRatings (user_id, instruction_id, rating) VALUES (?, ?, ?)",
                                        (user_id, instruction_id, user_rating))
                                self.con.commit()

                except sqlite3.Error as e:
                        print("Ошибка при обновлении рейтинга:", e)

                try:
                        # Получаем все рейтинги для данной инструкции
                        overall_rating = self.cursor.execute('SELECT rating FROM UserRatings WHERE instruction_id = ?',
                                                             (instruction_id,)).fetchall()

                        # Считаем общий рейтинг
                        sum_rating = sum(int(rating[0]) for rating in overall_rating)

                        if overall_rating:
                                # Вычисляем среднее значение рейтинга
                                average_rating = sum_rating / len(overall_rating)

                                # Обновляем общий рейтинг инструкции
                                self.cursor.execute('UPDATE Instruction SET rating = ? WHERE id = ?',
                                                    (average_rating, instruction_id))
                                self.con.commit()

                except sqlite3.Error as e:
                        print("Ошибка при вычислении или обновлении общего рейтинга:", e)


        def insert_count_of_clicks(self, instruction_id: int):
                """
                :param instruction_id: Инструкции айди
                """
                try:
                        self.cursor.execute('SELECT count_click FROM Instruction WHERE id = ?', (instruction_id,))
                        current_clicks = self.cursor.fetchone()

                        if current_clicks and isinstance(current_clicks[0], int):
                                new_click = current_clicks[0] + 1
                        else:
                                new_click = 1

                        self.cursor.execute("UPDATE Instruction SET count_click = ? WHERE id = ?",
                                            (new_click, instruction_id))
                        self.con.commit()
                except sqlite3.Error as e:
                        print("Ошибка при обновлении количества кликов:", e)


        def insert_suggestion(self, dict_suggestion: dict):
                """
                Добавляем в таблицу пожелания пользователей
                :param dict_suggetion: словарь значений
                """

                # Получаем айди пользователя в бд из его телеграм айди
                try:
                        self.cursor.execute('SELECT id FROM User WHERE user_tg_id = ?',
                                            (dict_suggestion['user_tg_id'],))
                        user_id = self.cursor.fetchone()
                        user_id = int(user_id[0])

                        # Проверяем, существует ли уже запись с таким пользователем и инструкцией
                        self.cursor.execute('SELECT id FROM UserSuggestions WHERE user_id = ? AND instruction_id = ?',
                                            (user_id, dict_suggestion['instruction_id']))
                        existing_suggestion = self.cursor.fetchone()

                        if existing_suggestion:
                                self.cursor.execute(
                                        'UPDATE UserSuggestions SET suggestion = ?, status = ? WHERE id = ?',
                                        (dict_suggestion['suggestion'], 'wait', existing_suggestion[0]))
                                self.con.commit()
                        else:
                                self.cursor.execute(
                                        'INSERT INTO UserSuggestions(user_id, instruction_id, suggestion, status) '
                                        'VALUES (?, ?, ?, ?)',
                                        (user_id, dict_suggestion['instruction_id'],
                                         dict_suggestion['suggestion'], 'wait'))
                                self.con.commit()

                except sqlite3.Error as e:
                        print("ошибка при добавлении предложения пользователя:", e)


        def get_suggestion(self):
            all_suggestion = self.cursor.execute('SELECT * FROM UserSuggestions').fetchall()

            return all_suggestion

        def add_program(self, name_program):
            """
            :param name_program: Название программы
            """

            self.cursor.execute(
                "INSERT INTO Program (program_name) VALUES (?)",
                (name_program,))
            self.con.commit()

        def delete_program(self, name_program):
                """
                :param name_program: Название программы
                """

                query = "DELETE FROM Program WHERE program_name = ?"
                self.cursor.execute(query, (name_program,))
                self.con.commit()

        def get_settings_column(self, program_name):
                """
                :param Название программы
                :return: Выгружает параграфы настроек, номер страницы
                """

                self.cursor.execute("SELECT paragraphs, page, image FROM SettingsParagraph "
                                    "INNER JOIN Program"
                                    "ON SettingsParagraph.program_id = Program.id"
                                    "WHERE program  ",(program_name,))







workDB = MethodsDB(con)
