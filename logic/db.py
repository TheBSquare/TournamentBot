from mysql.connector import connect, Error
from settings import *


class Db:
    host = db_host
    db_name = db_name
    users_table = db_users_table
    db_username = db_username
    db_password = db_password

    __connections = {}

    def __init__(self):
        self.create_connection(777)
        self.__create_users_table(777)
        self.close_connection(777)

    def add_user(self, connection_id, user_data):
        with self.__connections.get(connection_id).cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {self.users_table} (chatId, phoneNumber, paid, firstName, lastName, team)
                VALUES  (%s, %s, %s, %s, %s, %s)
                """, user_data
            )
            self.__connections.get(connection_id).commit()

    def check_user(self, connection_id, chat_id):
        with self.__connections.get(connection_id).cursor() as cursor:
            cursor.execute(f'SELECT EXISTS(SELECT chatId FROM {self.users_table} WHERE chatId = {chat_id})')
            return bool(cursor.fetchall()[0][0])

    def close_connection(self, connection_id):
        self.__connections.get(connection_id).close()

    def create_connection(self, connection_id):
        try:
            self.__connections[connection_id] = connect(
                host=self.host,
                user=self.__db_username,
                password=self.__db_password,
                database=self.db_name
            )
        except Error as e:
            raise e

    def get_users(self, connection_id):
        with self.__connections.get(connection_id).cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.users_table}")
            for user_data in cursor.fetchall():
                yield self.__row_to_dict(user_data)

    def get_user_by_chat_id(self, connection_id, chat_id):
        if not self.check_user(connection_id=connection_id, chat_id=chat_id):
            return None
        with self.__connections.get(connection_id).cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.users_table} WHERE chatId={chat_id}")
            user_data = cursor.fetchall()[0]
            return self.__row_to_dict(user_data)

    def change_user_data(self, connection_id, chat_id, key, new_data):
        with self.__connections.get(connection_id).cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE {self.users_table}
                SET {key} = {f"'{new_data}'" if type(new_data) is str else new_data}
                WHERE chatId = {chat_id}
                """)
            self.__connections.get(connection_id).commit()
    @staticmethod
    def __row_to_dict(data):
        return {x: data[i] for i, x in enumerate(('chatId', 'phoneNumber', 'paid', 'firstName', 'lastName', 'team'))}

    def __create_users_table(self, connection_id):
        with self.__connections.get(connection_id).cursor() as cursor:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.users_table} (
                    chatId BIGINT,
                    phoneNumber BIGINT,
                    paid TINYINT,
                    firstName VARCHAR(30),
                    lastName VARCHAR(30),
                    team VARCHAR(30)
                )
                """
            )
        self.__connections.get(connection_id).commit()


if __name__ == '__main__':
    db = Db()