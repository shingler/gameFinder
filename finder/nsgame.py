#!/usr/bin/python
# -*- coding:utf-8 -*-
# 数据库操作类
from finder.base import Games, Price

class SwitchJpGame(Games):

    def __init__(self):
        super(SwitchJpGame, self).__init__()
        self.platform = "switch"


class SwitchJpPrice(Price):

    def __init__(self):
        super(SwitchJpPrice, self).__init__()
        self.currency = "JPY"
        self.saleArea = "JP"
        self.url = "https://ec.nintendo.com/JP/ja/titles/%s"


class SwitchUSGame(Games):

    def __init__(self):
        super(SwitchUSGame, self).__init__()
        self.platform = "switch"


class SwitchUSPrice(Price):

    def __init__(self):
        super(SwitchUSPrice, self).__init__()
        self.currency = "USD"
        self.saleArea = "US"
        self.platform = "switch"
        self.url = "https://www.nintendo.com/games/detail/%s"


class SwitchHkGame(Games):

    def __init__(self):
        super(SwitchHkGame, self).__init__()
        self.platform = "switch"


class SwitchHkPrice(Price):

    def __init__(self):
        super(SwitchHkPrice, self).__init__()
        self.currency = "HKD"
        self.saleArea = "HK"
        self.platform = "switch"
        self.url = "https://www.nintendo.com.hk"


class SwitchZaGame(Games):

    def __init__(self):
        super(SwitchZaGame, self).__init__()
        self.platform = "switch"


class SwitchZaPrice(Price):

    def __init__(self):
        super(SwitchZaPrice, self).__init__()
        self.currency = "ZAR"
        self.saleArea = "ZA"
        self.platform = "switch"
        self.url = "https://www.nintendo.co.za"


def getFinder(platform, area):
    if platform == "switch" and str.lower(area) == "us":
        return SwitchUSPrice()
    if platform == "switch" and str.lower(area) == "jp":
        return SwitchJpPrice()
    if platform == "switch" and str.lower(area) == "hk":
        return SwitchHkPrice()
    if platform == "switch" and str.lower(area) == "za":
        return SwitchZaPrice()
