# 数据库类
import time

from db import Db


class Platform(Db):
    def __init__(self):
        self.id = 0
        self.platform = ""
        self.countryArea = ""
        self.countryAreaName = ""
        self.url = ""
        self.created = 0
        super(Platform, self).__init__()

    def get(self, platform, area, *args, **kwargs):
        sql = "SELECT * FROM game_finder.platforms WHERE platform='%s' AND countryArea='%s' ORDER BY platform" \
            % (platform, area)
        return super(Platform, self).find(sql)


class Price(Db):
    def __init__(self):
        self.id = 0
        self.officialGameId = 0
        self.subject = ""
        self.intro = ""
        self.cover = ""
        self.thumb = ""
        self.video = ""
        self.edition = ""
        self.publishDate = 0
        self.publishDateStr = ""
        self.players = 1
        self.rate = ""
        self.currency = "HKD"
        self.price = 0.0
        self.platform = ""
        self.saleArea = "HK"
        self.url = "https://store.playstation.com/zh-hant-hk/product/%s"
        self.latestPrice = 0.0
        self.plusPrice = 0.0
        self.latestExpire = 0
        self.plusExpire = 0
        self.historyPrice = 0.0
        self.hisDate = 0
        self.created = time.time()
        self.updated = time.time()
        super(Price, self).__init__()

    def getDataByOfficeGameId(self, officialGameId):
        sql_find = "SELECT * FROM game_finder.subjects WHERE officialGameId='%s'" % officialGameId
        # print(sql_find)
        data = super().find(sql_find)
        return data

    def getDataById(self, id):
        sql_find = "SELECT * FROM game_finder.subjects WHERE id='%s'" % id
        # print(sql_find)
        data = super().find(sql_find)
        return data

    def save(self):
        # 先查找是否存在
        exist = self.getDataByOfficeGameId(self.officialGameId)
        if exist:
            # 更新
            sql_update = "UPDATE game_finder.subjects SET "
            if float(exist["latestPrice"]) != self.latestPrice:
                sql_update += "latestPrice=%f, " % self.latestPrice
                sql_update += "latestExpire=%d," % self.latestExpire
            if float(exist["plusPrice"]) != self.plusPrice:
                sql_update += "plusPrice=%f," % self.plusPrice
                sql_update += "plusExpire=%d, " % self.plusExpire
            if float(exist["historyPrice"]) > self.latestPrice:
                sql_update += "historyPrice=%f, " % self.latestPrice
                sql_update += "hisDate=%d, " % time.time()
            if exist["publishDateStr"] != self.publishDateStr:
                sql_update += "publishDateStr=%s, " % self.publishDateStr
                sql_update += "publishDate=%d, " % int(self.publishDate)
            if exist["price"] != self.price:
                sql_update += "price=%f, " % self.price
            sql_update += "updated=%d" % time.time()
            sql_update += " WHERE id=%d"
            sql_update = sql_update % exist["id"]
            super().write(sql_update)
        else:
            # 插入
            sql_insert = """INSERT INTO game_finder.subjects (
                        officialGameId, subject, intro, cover, thumb, video, edition,
                        publishDate, publishDateStr, players, rate, currency, price, platform, 
                        saleArea, url, latestPrice, plusPrice, latestExpire, 
                        plusExpire, historyPrice, hisDate, created, updated) 
                        VALUES(
                        '{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}',
                        {7}, '{8}', '{9}', '{10}', '{11}', {12}, '{13}', 
                        '{14}', '{15}', {16}, {17}, {18}, 
                        {19}, {20}, {21}, {22}, {23}
                        )"""

            sql_insert = sql_insert.format(
                self.officialGameId, self.subject, self.intro, self.cover, self.thumb, self.video, self.edition,
                int(self.publishDate), self.publishDateStr, self.players, self.rate, self.currency, self.price,
                self.platform,
                self.saleArea, self.url, self.latestPrice, self.plusPrice, int(self.latestExpire),
                int(self.plusExpire), self.historyPrice, self.hisDate, self.created, self.updated
            )

            self.id = super().write(sql_insert)

        super().close()
        return self.id

    def delete(self, id):
        sql_delete = "DELETE FROM game_finder.subjects WHERE id='%s'" % id
        data = super().write(sql_delete)
        return True
