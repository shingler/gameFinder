#!/usr/bin/python
# -*- coding:utf-8 -*-
# switch游戏抓取父类
import json
import math
from abc import ABCMeta, abstractmethod

import requests


class Store(metaclass=ABCMeta):
    def __init__(self):
        self.currency = ""
        self.saleArea = ""
        self.url = ""
        self.count_url = ""
        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }

    # 获取游戏总数
    @abstractmethod
    def getCount(self, method="get", data={}, format="json"):
        if len(self.url) == 0:
            raise CountUrlEmptyError
        if method == "get":
            resp = requests.get(self.count_url, headers=self.headers)
        else:
            resp = requests.post(self.count_url, data=data, headers=self.headers)

        count_data = resp.text
        # 处理jsonp
        if format == "jsonp":
            count_data = resp.text
            count_data = count_data[count_data.find('(')+1:count_data.rfind(')')]

        json_data = json.loads(count_data, encoding="UTF-8")
        return json_data

    @abstractmethod
    def getData(self, size=1, page=1):
        pass

    # 获取总页数
    def getPage(self, size):
        total = self.getCount()
        return math.ceil(total / size)


class CountUrlEmptyError(RuntimeError):
    def __init__(self, args):
        self.args = args
