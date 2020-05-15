#!/usr/bin/python
# -*- coding:utf-8 -*-
# 获取货币汇率
import requests
import json
import sys
import time
sys.path.append("~/PycharmProjects/gameFinder/src")
from db import Db


class currency(Db):
    allowed_currency = ['JPY', 'USD', 'HKD', 'ZAR']
    to_currency = 'CNY'
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }
    db = {
        "db": "game_finder",
        "table": "currency"
    }

    def get_currency(self):
        # self._exchangeRate()
        self._nowapi()

    def _nowapi(self):
        # 免费版每小时50次调用，可免费试用3个月，到期可免费续（不推荐）
        # 免费版需要关联手机号
        # 接口可以指定货币名（推荐）
        # http://www.nowapi.com/api/finance.rate
        AppKey = '50870'
        Sign = 'ebfaf1e4da2776d4f68fb0e2a1732548'
        for src in self.allowed_currency:
            url = "https://sapi.k780.com"
            data = {
                "app": "finance.rate",
                "scur": src,
                "tcur": self.to_currency,
                "appkey": AppKey,
                "sign": Sign,
                "format": "json"
            }
            res = requests.post(url=url, data=data, headers=self.headers)
            # print(res.text)
            json_data = json.loads(res.text, encoding="UTF-8")
            if json_data["success"] == "1" and "result" in json_data:
                rate = float(json_data["result"]["rate"])
                updated = int(time.mktime(time.strptime(json_data["result"]["update"], "%Y-%m-%d %H:%M:%S")))

                query_sql = "SELECT * FROM %s.%s WHERE currency='%s'" % (self.db["db"], self.db["table"], src)
                res = self.find(query_sql)
                if res is None:
                    sql = "INSERT INTO %s.%s (currency, rate, updated) VALUES ('%s', %f, %d)"
                    sql = sql % (self.db["db"], self.db["table"], src, rate, updated)
                else:
                    sql = "UPDATE %s.%s SET rate=%f,updated=%d WHERE id=%d"
                    sql = sql % (self.db["db"], self.db["table"], rate, updated, res["id"])
                self.write(sql)


    def _fixer(self):
        # 免费版一个月只能访问1000次（合每天30次）
        # 免费版及基本版每小时更新，专业版分钟级更新
        # 免费版的基础货币不能更改，只有10刀每月的基本版可以修改。不推荐
        # fixer.io
        pass

    def _exchangeRate(self):
        # 公开版不需要API key。免费版可以修改基础货币，每月2000次调用。推荐
        # 免费版每日更新。付费版每小时更新（10刀/月起）
        # https://www.exchangerate-api.com/docs/standard-requests
        api_key = '18427c104d349d36d302b08c'
        for src in self.allowed_currency:
            url = "https://prime.exchangerate-api.com/v5/%s/latest/%s" % (api_key, src)
            res = requests.get(url=url, headers=self.headers)
            json_data = json.loads(res.text, encoding="UTF-8")
            if "conversion_rates" in json_data:
                rate = json_data["conversion_rates"][self.to_currency]
                updated = json_data["time_last_update"]

                query_sql = "SELECT * FROM %s.%s WHERE currency='%s'" % (self.db["db"], self.db["table"], src)
                res = self.find(query_sql)
                if res is None:
                    sql = "INSERT INTO %s.%s (currency, rate, updated) VALUES ('%s', %f, %d)"
                    sql = sql % (self.db["db"], self.db["table"], src, rate, updated)
                else:
                    sql = "UPDATE %s.%s SET rate=%f,updated=%d WHERE id=%d"
                    sql = sql % (self.db["db"], self.db["table"], rate, updated, res["id"])
                self.write(sql)

    def _juhe(self):
        # 该API适合做外汇汇率投资曲线图，不适合本项目需求
        pass

def main():
    cur = currency()
    cur.get_currency()


if __name__ == "__main__":
    main()
