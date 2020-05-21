# 媒体评分内容抓取父类
import time
import requests
import urllib3

from db import Db


class Spider:
    platform = ['switch', 'ps4']

    def __init__(self, host, magazine):
        self.host = host
        self.magazine = magazine
        self.info = {
            "gameId": 0,    # 需要后续人工关联
            "magazine": self.magazine,
            "score": 0.0,
            "scoreWord": "",
            "subject": "",
            "comment": "",
            "url": "",
            "created": int(time.time())
        }

    @staticmethod
    def http(url):
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.117 Safari/537.36',
        }
        print(url)
        urllib3.disable_warnings()
        urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass

        resp = requests.get(url, headers=header, timeout=60, verify=False)
        print(resp.status_code)
        if resp.status_code == requests.codes.ok:
            return resp
        elif resp.status_code == 404:
            return None
        else:
            resp.raise_for_status()

    # 根据内容抓取数据
    def parse(self, content):
        pass

    # 根据内容抓取详情页
    def parseDetail(self, data):
        pass

    # 保存数据入库
    def save(self, data):
        lastId = 0
        # 查找重复
        exist = self.ifExists(data["url"])
        if not exist:
            sql_insert = """INSERT INTO game_finder.magzine_scores(
            gameId, magazine, score, scoreWord, subject, comment, url, created, comment_trans) VALUES (
            %d, '%s', %f, '%s', '%s', '%s', '%s', %d, ''
            )"""
            sql_insert = sql_insert % (data["gameId"], data["magazine"], data["score"], data["scoreWord"],
                     data["subject"], data["comment"], data["url"], data["created"])
            # print(sql)

            db = Db()
            lastId = db.write(sql_insert)
            db.close()
        else:
            sql_update = """UPDATE game_finder.magzine_scores SET score=%d,scoreWord='%s',
            subject='%s', comment='%s', url='%s' WHERE id=%d"""
            sql_update = sql_update % (data["score"], data["scoreWord"], data["subject"],
                                       data["comment"], data["url"], exist)
            db = Db()
            db.write(sql_update)
            db.close()
            lastId = exist
        return lastId

    # 检查是否存在
    def ifExists(self, url):
        # 条件：相同url且内容非空，则认为是同一款游戏，防止重复写库
        sql_check = "SELECT * FROM game_finder.magzine_scores WHERE url='%s' and comment!=''" % url
        db = Db()
        exist = db.find(sql_check)
        db.close()
        if exist is not None:
            return exist["id"]
        else:
            return False
