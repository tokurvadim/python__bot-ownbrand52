import sqlite3 as sq
import json
from pprint import pprint
from aiogram.types.input_file import FSInputFile


class DataBase:
    def __init__(self, patch: str):
        self._patch = patch

    def create_table_user(self):
        self.get_cursor.execute("""CREATE TABLE IF NOT EXISTS User (
                                            user_telegram_id INT NOT NULL,
                                        
                                            last_bot_message_id INT DEFAULT 0,
                                            user_group_joined BOOL DEFAULT False,
                                            status INTEGER DEFAULT 0,
                                            subscribe INTEGER DEFAULT 0
                                           )""")
        return 1
    

    def create_table_price(self):
        self.get_cursor.execute("""CREATE TABLE IF NOT EXISTS Price (
                                            days INT NOT NULL,
                                            price INT NOT NULL
                                           )""")
        self.set_table_price()

        return 1
    
    def create_tables(self):
        self.create_table_user()
        self.create_table_price()
        return
    
    def set_table_price(self):
        prices = self.get_cursor.execute('SELECT * FROM Price').fetchall()
        if not prices:
            for price in self.get_price_data().items():
                self.get_cursor.execute(f"INSERT INTO Price(days, price) VALUES ({price[0]}, {price[1]});").connection.commit()
        return

    def get_table_price(self) -> list[tuple]:
        prices: list[tuple] = self.get_cursor.execute('SELECT * FROM Price').fetchall()
        return prices
    
    def update_user_subscribe(self, user_telegram_id: int, subscribe: int):
        self.get_cursor.execute(f'UPDATE User SET subscribe=subscribe+? WHERE user_telegram_id=?', (subscribe, user_telegram_id)).connection.commit()
        return
    
    def get_user_status(self, user_telegram_id: int) -> int:
        print(user_telegram_id)
        status = self.get_cursor.execute(f'SELECT status FROM User WHERE user_telegram_id={user_telegram_id}').fetchone()
        return status
    
    def get_user_subscribe(self, user_telegram_id: int) -> int:
        subscribe = self.get_cursor.execute(f'SELECT subscribe FROM User WHERE user_telegram_id={user_telegram_id}').fetchone()
        return subscribe

    def get_buttons_locked(self, user_telegram_id: int):
        result = self.get_cursor.execute("SELECT user_buttons_locked FROM User WHERE user_telegram_id = ?",
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
    def get_price_data() -> dict:
        with open('bot/data/settings.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_last_bot_message_id(self, user_telegram_id: int) -> str:
        result = self.get_cursor.execute("SELECT last_bot_message_id FROM Data WHERE user_telegram_id = ?",(user_telegram_id,), ).fetchone()
        return result[0]

    def set_last_bot_message_id(self, user_telegram_id: int, last_bot_message_id: int) -> None:
        self.get_cursor.execute('UPDATE User SET last_bot_message_id = ? WHERE user_telegram_id = ?;',(last_bot_message_id, user_telegram_id)).connection.commit()

    def set_group_joined_true(self, user_telegram_id: int):
        self.get_cursor.execute('UPDATE User SET user_group_joined = ? WHERE user_telegram_id = ?;',(True, user_telegram_id)).connection.commit()

    def get_user_group_joined(self, user_telegram_id: str) -> bool:
        result = self.get_cursor.execute("SELECT user_group_joined FROM User WHERE user_telegram_id = ?",
                                         (user_telegram_id,), ).fetchone()
        if result[0] == 0:
            return False
        else:
            return True



    def add_user(self, user_telegram_id: str):
        user_data = self.get_cursor.execute("SELECT * FROM User WHERE user_telegram_id = ?", (user_telegram_id,),).fetchone()
        if user_data is None:
            # Создаём нового юзера если его нет в бд
            self.get_cursor.execute('INSERT INTO User (user_telegram_id) VALUES (?);', (user_telegram_id,)).connection.commit()

            print(f'Бота запустил новый пользователь {user_telegram_id}')
            return True
        
    def update_user_status(self, user_telegram_id: str, status: id):
        self.get_cursor.execute("UPDATE User SET status = ? WHERE user_telegram_id = ?", (status, user_telegram_id)).connection.commit()
        return


    def get_img(self, name: str) -> FSInputFile:
        return FSInputFile(f'data/imgs/{name}')

    def get_json(self, name: str) -> FSInputFile:
        return FSInputFile(f'data/imgs/{name}')

    @property
    def get_cursor(self):
        with sq.connect(self._patch) as con:
            return con.cursor()
