# 写数据库的配置信息
from configparser import ConfigParser


class Config:
    db = dict()

    def __init__(self):
        cfg = ConfigParser()
        cfg.read("config.ini")
        env = cfg.get("default", "env.default")

        self.db["host"] = cfg.get(env, "database.host")
        self.db["user"] = cfg.get(env, "database.username")
        self.db["pwd"] = cfg.get(env, "database.password")
        self.db["db_name"] = cfg.get(env, "database.db_name")
