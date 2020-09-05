#!/usr/bin/python
# -*- coding:utf-8 -*-
# 从PS4港服获取最新游戏信息及数字版价格
import json
import time

import requests

from finder.base import Platform
from finder.store import Store
from finder import ps4game


class PS4Hk(Store):

    def __init__(self):
        super(PS4Hk, self).__init__()
        platform_obj = Platform()
        platform_ps4_hk = platform_obj.get(platform="PS4", area="HK")

        self.list_url = platform_ps4_hk["url"]
        self.currency = "HKD"
        self.saleArea = platform_ps4_hk["countryArea"]
        self.url = "https://store.playstation.com/zh-hant-hk/product/%s"
        self.count_url = self.list_url % (0, 0)

    # 获取游戏总数
    def getCount(self):
        data_list = super(PS4Hk, self).getCount(method="get", format="json")
        # 总数
        total = data_list["data"]["attributes"]["total-results"]
        return total

    # 获取某个列表的数据列表
    def getPageData(self, size=1, page=1):
        offset = (page - 1) * size
        url = self.list_url % (size, offset)
        print(url)

        resp = requests.get(url, headers=self.headers)
        data_list = json.loads(resp.text, encoding="UTF-8")
        return data_list

    # 保存一个数据入库
    def storeData(self, data):
        # 查找游戏资料是否存在
        game = ps4game.getFinder("ps4", self.saleArea)
        # officialGameId = data["id"][0:data["id"].rfind("-")]
        officialGameId = data["id"]

        # 新增数据
        info = data["attributes"]
        game.officialGameId = officialGameId
        game.subject = info["name"].replace("'", "\\\'")
        game.intro = info["long-description"].replace("'", "\\\'")
        game.cover = info["thumbnail-url-base"]
        # 截图记录
        if "screenshots" in info["media-list"]:
            game.thumb = []
            for ss in info["media-list"]["screenshots"]:
                game.thumb.append(ss["url"])
            game.thumb = json.dumps(game.thumb)
        # 记录多个地址
        if "preview" in info["media-list"]:
            game.video = []
            for pv in info["media-list"]["preview"]:
                game.video.append(pv["url"])
            game.video = json.dumps(game.video)

        game.publishDate = int(time.mktime(time.strptime(info["release-date"], "%Y-%m-%dT%H:%M:%SZ"))) if info[
            "release-date"] else 0
        game.publishDateStr = info["release-date"][:info["release-date"].find("T")]

        # 游戏价格
        if "skus" in data["attributes"]:
            # 大部分游戏在skus里只有一个对象。但是有的游戏有体验版，会出现2个。
            # 体验版一般是第二个，所以我们只拿第一个即可。
            one = data["attributes"]["skus"][0]
            game.platform = "ps4"
            game.edition = one["name"] if "name" in one else ""
            game.price = 0.0
            game.currency = self.currency
            game.saleArea = self.saleArea
            game.url = self.url % game.officialGameId
            game.latestPrice = one["prices"]["non-plus-user"]["actual-price"]["value"] * 0.01
            game.plusPrice = one["prices"]["plus-user"]["actual-price"]["value"] * 0.01

            # 原价逻辑稍微复杂。如果存在折扣需要额外获取
            if one["prices"]["non-plus-user"]["strikethrough-price"]:
                game.price = one["prices"]["non-plus-user"]["strikethrough-price"]["value"] * 0.01
            else:
                game.price = game.latestPrice

            latestExpire = one["prices"]["non-plus-user"]["availability"]["end-date"]
            if latestExpire is None:
                game.latestExpire = 0
            else:
                game.latestExpire = int(time.mktime(time.strptime(latestExpire, "%Y-%m-%dT%H:%M:%SZ")))
            # print(price.latestExpire)
            plusExpire = one["prices"]["plus-user"]["availability"]["end-date"]
            if plusExpire is None:
                game.plusExpire = 0
            else:
                game.plusExpire = int(time.mktime(time.strptime(plusExpire, "%Y-%m-%dT%H:%M:%SZ")))

            game.historyPrice = game.latestPrice
            game.hisDate = int(time.time())
            game.created = int(time.time())
            game.updated = int(time.time())

            game.save()
            return game.id

    # 爬虫入口
    def getData(self, size=1, page=1):
        data_list = self.getPageData(size, page)

        for data in data_list["included"]:
            # 游戏资料
            if data["type"] == "game":
                # 保存入库
                self.storeData(data)
                # exit(1)
