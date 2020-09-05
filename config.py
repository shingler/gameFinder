# 写数据库的配置信息
from configparser import ConfigParser
import os
import const

class Config:
    db = dict()

    def __init__(self):
        config_path = const.ROOT_PATH + "/config.ini"
        if not os.path.exists(config_path):
            raise FileNotFoundError("the config.ini not found")
        cfg = ConfigParser()
        cfg.read(config_path)
        # print(cfg.sections())
        env = cfg.get("default", "env.default")

        self.db["host"] = cfg.get(env, "database.host")
        self.db["user"] = cfg.get(env, "database.username")
        self.db["pwd"] = cfg.get(env, "database.password")
        self.db["db_name"] = cfg.get(env, "database.db_name")
