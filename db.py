import pymysql
from config import Config


class Db:
    def __init__(self):
        config = Config()
        self.con = pymysql.connect(config.db["host"], config.db["user"], config.db["pwd"], config.db["db_name"], cursorclass=pymysql.cursors.DictCursor)

    def close(self):
        self.con.close()

    def write(self, sql):
        # print(sql)
        # exit(1)
        cursor = self.con.cursor()
        lastId = 0
        try:
            cursor.execute(sql)
            lastId = int(cursor.lastrowid)
            self.con.commit()
        except:
            print(sql)

        return lastId

    def query(self, sql):
        cursor = self.con.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    def find(self, sql):
        cursor = self.con.cursor()
        try:
            cursor.execute(sql)
        except:
            print(sql)
        else:
            data = cursor.fetchone()
            return data

    def rowCount(self, sql):
        cursor = self.con.cursor()
        cursor.execute(sql)
        count = cursor.rowcount
        return count