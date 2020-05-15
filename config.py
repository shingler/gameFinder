# 写数据库的配置信息
class Config:
    db = dict()

    def __init__(self):
        self.db["host"] = "localhost"
        self.db["user"] = "root"
        self.db["pwd"] = "123456"
        self.db["db_name"] = "game_finder"
