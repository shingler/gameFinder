#!/usr/bin/python
# -*- coding:utf-8 -*-
# 从switch南非服获取游戏数据并入库
# 南非服会先请求欧洲服，拿到跨域的jsonp数据
# https://searching.nintendo-europe.com/za/select?q=*&fq=type:GAME AND ((price_has_discount_b:"true")) AND sorting_title:* AND *:*&sort=score desc, date_from desc&start=0&rows=24&wt=json&bf=linear(ms(priority,NOW/HOUR),1.1e-11,0)&bq=deprioritise_b:true^-1000&json.wrf=nindo.net.jsonp.jsonpCallback_3931_2900000368245
# 再请求price的json请求
# https://api.ec.nintendo.com/v1/price?country=ZA&lang=en&ids=70010000019341,70010000023393,70010000023216,70010000026964,70010000027295,70010000021894,70010000028454,70010000028601,70010000016888,70010000026411,70010000028069,70010000021726,70010000025434,70010000025749,70010000028847,70010000026867,70010000026796,70010000021478,70010000028043,70010000028361,70010000028081,70010000029030,70010000023218,70010000027958
import json
import time

import requests
from bs4 import BeautifulSoup

from finder import nsgame
from finder.store import Store


class SwitchZa(Store):
    saleArea = 'ZA'
    currency = 'ZAR'
    url = 'https://www.nintendo.co.za%s'
    price_url = 'https://api.ec.nintendo.com/v1/price?country=ZA&lang=en&ids=%s'

    def getCount(self, method="get", data=None, format="json"):
        self.count_url = self.list_url.format(0, 1)
        json_data = super(SwitchZa, self).getCount(format="jsonp")
        total = json_data["response"]["numFound"]
        return total

    def getPageData(self, size=1, page=1) -> list:
        offset = (page - 1) * size
        url = self.list_url.format(offset, size)

        resp = requests.get(url, headers=self.headers, allow_redirects=False)
        # 南非服从欧服拿东西，格式是jsonp
        resp_text = resp.text[resp.text.find("(") + 1:resp.text.rfind(")")]
        json_data = json.loads(resp_text, encoding="UTF-8")
        data_list = json_data["response"]["docs"]
        return data_list

    def saveData(self, data, for_test=False) -> int:
        if "nsuid_txt" not in data:
            return 0

        officialGameId = data["nsuid_txt"][0]
        if for_test:
            officialGameId = "fake_" + officialGameId

        price_obj = nsgame.getFinder("switch", str.lower(self.saleArea))

        # 是否存在。如果存在就不爬详情页了，节约时间
        exist = price_obj.getDataByOfficeGameId(officialGameId)

        price_obj.officialGameId = "fake_" + officialGameId if for_test else officialGameId
        price_obj.subject = data["title"].replace("'", "\\\'")
        price_obj.intro = data["excerpt"].replace("'", "\\\'")
        price_obj.cover = "https:%s" % data["image_url"] if "image_url" in data else ""
        price_obj.video = ""
        # 未发售游戏的发售日无法转换
        price_obj.publishDateStr = data["dates_released_dts"][0]
        # print(price_obj.publishDateStr)
        if "T" in price_obj.publishDateStr:
            date_str = price_obj.publishDateStr[:price_obj.publishDateStr.rfind("T")]
            price_obj.publishDateStr = date_str
            try:
                price_obj.publishDate = int(time.mktime(time.strptime(date_str, "%Y-%m-%d")))
            except:
                pass
        if "players_from" in data:
            price_obj.players = "%s - %s" % (data["players_from"], data["players_to"])
        else:
            price_obj.players = data["players_to"]
        price_obj.platform = "switch"
        price_obj.edition = data["language_availability"][0]
        # 没有发售日期的游戏没有价格
        price_obj.price = data["price_regular_f"] if ("price_regular_f" in data) else -1

        price_obj.url = self.url % data["url"]
        price_obj.rate = "%s : %s" % (data["age_rating_type"], data["age_rating_value"])

        # 获取价格
        self.getSalePrice(price_obj, officialGameId)

        # 获取截图
        if not exist:
            self.getDetail(price_obj, price_obj.url)

        price_obj.historyPrice = price_obj.latestPrice  # 保存的时候会检查
        price_obj.hisDate = int(time.time())
        price_obj.created = int(time.time())
        price_obj.updated = int(time.time())

        print("%s saved." % price_obj.subject)
        return price_obj.save()

    # 获取折扣价
    def getSalePrice(self, price_obj, officialGameIds):
        url = self.price_url % officialGameIds
        resp = requests.get(url, headers=self.headers, allow_redirects=False)
        json_data = json.loads(resp.text, encoding="UTF-8")
        if "prices" in json_data:
            price_data = json_data["prices"][0]
            if "discount_price" in price_data:
                price_obj.latestPrice = float(price_data["discount_price"]["raw_value"])
                price_obj.latestExpire = time.mktime(time.strptime(price_data["discount_price"]["end_datetime"], "%Y-%m-%dT%H:%M:%SZ"))
            elif "regular_price" in price_data:
                price_obj.latestPrice = float(price_data["regular_price"]["raw_value"])
                price_obj.latestExpire = -1

    # 进入详情页获取游戏截图
    def getDetail(self, price_obj, url):
        resp = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        grid = soup.find("ul", class_="results tc-xs-grid card-grid")
        if grid:
            list = grid.find_all("li")
            price_obj.thumb = []
            for one in list:
                img = "https:%s" % one.find("img", class_="img-responsive").attrs["data-xs"]
                price_obj.thumb.append(img.replace("_TM_Standard", ""))
            price_obj.thumb = json.dumps(price_obj.thumb)
