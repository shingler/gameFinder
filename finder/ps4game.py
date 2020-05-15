#!/usr/bin/python
# -*- coding:utf-8 -*-
from finder.base import Games, Price


class PS4HkGame(Games):

    def __init__(self):
        super(PS4HkGame, self).__init__()
        self.platform = "ps4"


class PS4HkPrice(Price):

    def __init__(self):
        super(PS4HkPrice, self).__init__()
        self.currency = "HKD"
        self.saleArea = "HK"
        self.url = "https://store.playstation.com/zh-hant-hk/product/%s"


def getFinder(platform, area):
    if platform == "ps4" and str.lower(area) == "hk":
        return PS4HkPrice()
