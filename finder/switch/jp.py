# 从switch日服获取游戏数据并入库
import time
import requests
import json

from finder import nsgame
from finder.store import Store


class SwitchJp(Store):
    currency = "JPY"
    saleArea = "JP"
    url = "https://ec.nintendo.com/JP/ja/titles/%s"

    def getCount(self, method="get", data=None, format="json"):
        self.count_url = self.list_url.format(0, 1)
        json_data = super(SwitchJp, self).getCount()
        # 总数
        total = int(json_data["result"]["total"])
        return total

    def getPageData(self, size=1, page=1) -> list:
        url = self.list_url
        url = url.format(size, page)
        # print(url)
        resp = requests.get(url, headers=self.headers, allow_redirects=False)
        data_list = json.loads(resp.text, encoding="UTF-8")
        return data_list["result"]["items"]

    def saveData(self, data, for_test=False) -> int:
        # 游戏资料
        officialGameId = data["id"]

        # 游戏价格
        price_obj = nsgame.getFinder(platform="switch", area=str.lower(self.saleArea))
        price_obj.officialGameId = "fake_" + officialGameId if for_test else officialGameId
        price_obj.subject = data["title"].replace("'", "\\\'")
        price_obj.intro = data["text"].replace("'", "\\\'")
        price_obj.cover = "https://img-eshop.cdn.nintendo.net/i/%s.jpg" % data["iurl"]
        price_obj.video = ""
        price_obj.publishDate = int(time.mktime(time.strptime(data["sdate"], "%Y.%m.%d")))
        price_obj.publishDateStr = data["sdate"]
        price_obj.players = data["player"][0] if data["player"] else 1
        price_obj.platform = "switch"
        price_obj.edition = "日文版"
        # price_obj.edition = data["sform_n"]
        price_obj.price = data["price"]
        price_obj.url = price_obj.url % officialGameId
        price_obj.latestPrice = data["current_price"]
        price_obj.plusPrice = data["current_price"]
        price_obj.rate = "CERO : %s" % data["cero"][0] if data["cero"] else ""

        latestExpire = data["ssdate"] if "ssdate" in data else None
        if latestExpire is None:
            price_obj.latestExpire = 0
        else:
            price_obj.latestExpire = int(time.mktime(time.strptime(latestExpire, "%Y-%m-%d %H:%M:%S")))
        # print(price.latestExpire)
        price_obj.plusExpire = 0

        price_obj.historyPrice = price_obj.latestPrice
        price_obj.hisDate = time.time()
        price_obj.created = time.time()
        price_obj.updated = time.time()

        return price_obj.save()

    def getDetail(self, price_obj, url) -> None:
        pass
