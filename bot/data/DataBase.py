import sqlite3 as sq
import json
from pprint import pprint
from aiogram.types.input_file import FSInputFile


class DataBase:
    def __init__(self, patch: str):
        self._patch = patch

    def create_table(self):
        self.get_cursor.execute("""CREATE TABLE IF NOT EXISTS Data (
                                            user_telegram_id INT NOT NULL,
                                            
                                            user_buttons_locked TEXT DEFAULT '[]',
                                        
                                            last_bot_message_id INT DEFAULT 0,
                                            user_group_joined BOOL DEFAULT False
                                           )""")
        return 1

    def get_buttons_locked(self, user_telegram_id: int):
        result = self.get_cursor.execute("SELECT user_buttons_locked FROM Data WHERE user_telegram_id = ?",
                                         (user_telegram_id,), ).fetchone()
        return json.loads(result[0])

    def switch_buttons_locked(self, user_telegram_id: int, name: str):
        buttons_locked = self.get_buttons_locked(user_telegram_id=user_telegram_id)
        if name in buttons_locked:
            buttons_locked.remove(name)
        else:
            buttons_locked.append(name)
        self.get_cursor.execute('UPDATE Data SET user_buttons_locked = ? WHERE user_telegram_id = ?;',(json.dumps(buttons_locked), user_telegram_id)).connection.commit()



    @staticmethod
    def get_buttons_data():
        with open('data/settings.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_last_bot_message_id(self, user_telegram_id: int) -> str:
        result = self.get_cursor.execute("SELECT last_bot_message_id FROM Data WHERE user_telegram_id = ?",(user_telegram_id,), ).fetchone()
        return result[0]

    def set_last_bot_message_id(self, user_telegram_id: int, last_bot_message_id: int) -> None:
        self.get_cursor.execute('UPDATE Data SET last_bot_message_id = ? WHERE user_telegram_id = ?;',(last_bot_message_id, user_telegram_id)).connection.commit()

    def set_group_joined_true(self, user_telegram_id: int):
        self.get_cursor.execute('UPDATE Data SET user_group_joined = ? WHERE user_telegram_id = ?;',(True, user_telegram_id)).connection.commit()

    def get_user_group_joined(self, user_telegram_id: str) -> bool:
        result = self.get_cursor.execute("SELECT user_group_joined FROM Data WHERE user_telegram_id = ?",
                                         (user_telegram_id,), ).fetchone()
        if result[0] == 0:
            return False
        else:
            return True


    def add_user(self, user_telegram_id: str):
        user_data = self.get_cursor.execute("SELECT * FROM Data WHERE user_telegram_id = ?", (user_telegram_id,),).fetchone()
        if user_data is None:
            # Создаём нового юзера если его нет в бд
            self.get_cursor.execute('INSERT INTO Data (user_telegram_id) VALUES (?);', (user_telegram_id,)).connection.commit()

            print(f'Бота запустил новый пользователь {user_telegram_id}')
            return True

    def get_img(self, name: str) -> FSInputFile:
        return FSInputFile(f'data/imgs/{name}')

    def get_json(self, name: str) -> FSInputFile:
        return FSInputFile(f'data/imgs/{name}')

    @property
    def get_cursor(self):
        with sq.connect(self._patch) as con:
            return con.cursor()
