#!/usr/bin/python
# -*- coding:utf-8 -*-
# 从港服抓取数据
# 喂喂喂，港服也太那个了吧。虽说游戏少，你一上来就把所有数据的json传过来也太省事了吧
# https://www.nintendo.com.hk/data/json/switch_software.json?418544271551
import json
import time
import requests
from bs4 import BeautifulSoup

from finder import nsgame
from finder.base import Platform
from finder.store import Store


class SwitchHk(Store):
    def __init__(self):
        super(SwitchHk, self).__init__()
        platform_obj = Platform()
        platform_data = platform_obj.get(platform="switch", area="HK")

        self.list_url = platform_data["url"]
        self.currency = "HKD"
        self.saleArea = platform_data["countryArea"]
        self.url = "https://www.nintendo.com.hk%s"
        self.count_url = self.list_url

    def getCount(self):
        # 就一页，还分什么页
        return 999999

    def getPageData(self, size, page):
        # 港服就一个大json，暂时用不到size和page
        url = self.list_url

        resp = requests.get(url, headers=self.headers, allow_redirects=False)
        data_list = json.loads(resp.text, encoding="UTF-8")
        result = []

        # 只抓取eshop数据
        for data in data_list:
            if data["media"] != "eshop":
                continue
                # link不带域名的是硬件，也跳过
            if not data["link"].startswith("http"):
                continue
            result.append(data)

        return data_list

    def saveData(self, data, for_test=False):
        # 游戏资料
        # id没有直接给出，而是在url里
        officialGameId = data["link"][str.rfind(data["link"], "/") + 1:]
        print(officialGameId)
        if for_test:
            officialGameId = "fake_" + officialGameId

        # 游戏价格
        price_obj = nsgame.getFinder(platform="switch", area=str.lower(self.saleArea))
        price_obj.officialGameId = officialGameId
        price_obj.subject = data["title"].replace("'", "\\\'")
        price_obj.intro = ""
        price_obj.cover = "https://www.nintendo.com.hk/software/img/bnr/%s" % data["thumb_img"]
        price_obj.video = ""
        price_obj.publishDate = int(time.mktime(time.strptime(data["release_date"], "%Y.%m.%d")))
        price_obj.publishDateStr = data["release_date"]
        price_obj.players = 1
        price_obj.platform = "switch"
        # price_obj.edition = ""
        price_obj.edition = data["lang"]
        price_obj.price = data["price"]
        price_obj.url = data["link"]
        # price_obj.latestPrice = data["current_price"]
        # price_obj.plusPrice = data["current_price"]
        # price_obj.rate = "CERO : %s" % data["cero"][0] if data["cero"] else ""

        # latestExpire = data["sale_until"] if "sale_until" in data else None
        # if latestExpire is None:
        #     price_obj.latestExpire = 0
        # else:
        #     price_obj.latestExpire = int(time.mktime(time.strptime(latestExpire, "%Y-%m-%d %H:%M:%S")))
        # print(price.latestExpire)
        price_obj.plusExpire = 0

        price_obj.historyPrice = price_obj.latestPrice
        # price_obj.hisDate = time.strftime("%Y-%m-%d")
        price_obj.hisDate = int(time.time())
        price_obj.created = int(time.time())
        price_obj.updated = int(time.time())
        self.getDetail(price_obj, data["link"])

        print("%s saved." % price_obj.subject)
        return price_obj.save()

    def getDetail(self, price_obj, url):
        url = str(url)
        if not url.startswith("http"):
            url = self.url % url
        print(url)
        resp = requests.get(url, headers=self.headers, allow_redirects=False)
        soup = BeautifulSoup(resp.text, "html.parser")
        # 游戏介绍
        desc = soup.find("div", class_="product attribute description")
        if desc is not None:
            price_obj.intro = desc.find("div", class_="value").text
        # 游戏人数
        player_data = soup.find("div", class_="product-attribute no_of_players")
        if player_data is not None:
            price_obj.players = player_data.find("div", class_="product-attribute-val").text
        # 支持语言
        langs = soup.find("div", class_="product-attribute supported_languages")
        if langs is not None:
            price_obj.edition = langs.find("div", class_="product-attribute-val").text

        # 价格
        product_data = soup.find("div", class_="product-page-info")
        price = float(product_data.find("meta", {"itemprop": "price"}).attrs["content"])
        # 港服暂时没有发现折扣活动
        price_obj.price = price
        price_obj.latestPrice = price
        price_obj.plusPrice = price
        price_obj.latestExpire = 0

        # 获取截图 港服图片是写在script里，然后懒加载实现的
        script_data = soup.find_all("script", type="text/x-magento-init")

        price_obj.thumb = []
        for li in script_data:
            # print(li, li.string)

            li = json.loads(li.string)
            if "[data-gallery-role=gallery-placeholder]" in li:
                gallery = li["[data-gallery-role=gallery-placeholder]"]
                if "mage/gallery/gallery" in gallery:
                    img_gallery = gallery["mage/gallery/gallery"]
                    if "data" in img_gallery:
                        for img in img_gallery["data"]:
                            price_obj.thumb.append(img["img"])
        price_obj.thumb = json.dumps(price_obj.thumb)

    # 目前港服就一页，需要直接返回1，免得停不下来
    def getPage(self, size):
        return 1
