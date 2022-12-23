import sqlite3
import datetime


class DataBase:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def clear(self, m=3):
        self.cursor.execute("DELETE FROM accounts WHERE date <= ?",
                            (datetime.datetime.now() - datetime.timedelta(minutes=m),))
        self.connection.commit()

    def get_all(self):
        return self.cursor.execute("SELECT * FROM accounts")

    def add(self, r_url, headers, cookies, proxy, video_id):
        self.cursor.execute(
            "INSERT INTO accounts (r_url, headers, cookies, proxy, video_id, date) VALUES (?, ?, ?, ?, ?, ?)",
            (r_url, headers, cookies, proxy, video_id, datetime.datetime.now())
        )
        self.connection.commit()

    def remove(self, id):
        self.cursor.execute("DELETE FROM accounts WHERE (id = ?)", (id,))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
