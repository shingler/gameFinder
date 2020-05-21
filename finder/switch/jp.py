# 从switch日服获取游戏数据并入库
import time
import requests
import json

from finder import nsgame
from finder.store import Store


class SwitchJp(Store):

    def __init__(self):
        super(SwitchJp, self).__init__()
        self.currency = "JPY"
        self.saleArea = "JP"
        self.url = "https://ec.nintendo.com/JP/ja/titles/%s"
        self.count_url = "https://search.nintendo.jp/nintendo_soft/search.json?opt_sshow=1&fq=ssitu_s%3Aonsale%20OR%20ssitu_s%3Apreorder%20OR%20(%20id%3A3347%20OR%20id%3A70010000013978%20OR%20id%3A70010000005986%20OR%20id%3A70010000004356%20OR%20id%3Aef5bf7785c3eca1ab4f3d46a121c1709%20OR%20id%3A3252%20OR%20id%3A3082%20)&limit=0&page=1&c=14316436013423625&opt_osale=1&opt_hard=1_HAC&sort=sodate%20desc%2Cscore"

    def getCount(self):
        json_data = super(SwitchJp, self).getCount()
        # 总数
        total = int(json_data["result"]["total"])
        return total

    # 获取游戏资料
    def getData(self, size=1, page=1):
        url = "https://search.nintendo.jp/nintendo_soft/search.json?opt_sshow=1&fq=ssitu_s:onsale%20OR%20ssitu_s:preorder&limit={0}&page={1}&c=14316436013423625&opt_osale=1&opt_hard=1_HAC&sort=sodate%20desc,score"
        url = url.format(size, page)
        # print(url)
        resp = requests.get(url, headers=self.headers, allow_redirects=False)
        data_list = json.loads(resp.text, encoding="UTF-8")

        for data in data_list["result"]["items"]:
            # 游戏资料
            officialGameId = data["id"]

            # 游戏价格
            price_obj = nsgame.getFinder(platform="switch", area=str.lower(self.saleArea))
            price_obj.officialGameId = officialGameId
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

            price_obj.save()
            # break
