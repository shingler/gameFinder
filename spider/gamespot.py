# 从gamespot上抓取游戏评分
import os

import bs4
from bs4 import BeautifulSoup

from spider.spider import Spider


class Gamespot(Spider):
    platform = ['PS4', 'NS']

    def __init__(self):
        host = "https://www.gamespot.com"
        magazine = "gamespot"
        super(Gamespot, self).__init__(host, magazine)

    # 解析列表，抓取评分，标题
    def parse(self, content):
        soup = BeautifulSoup(content.text, "html.parser")

        games = soup.find_all("div", {"class": "horizontal-card-item"})

        for item in games:
            # 如果已入库就不重复获取详情了
            url = self.host + item.find_all("a", class_="horizontal-card-item__link")[0].attrs["href"]
            if bool(self.ifExists(url)):
                continue

            # 抓取指定平台的作品，这个有可能是多平台，用逗号分隔的
            plat_str = item.find("span", class_="horizontal-card-item__label").string
            # 无平台信息，跳过
            if plat_str is None:
                continue
            plat_list = plat_str.split(',')

            is_in_platform = False
            for p in plat_list:
                if p in self.platform:
                    is_in_platform = True
                    break

            if not is_in_platform:
                continue

            # 评测信息
            self.info["score"] = float(item.find("div", class_="review-ring-score__score").string)
            self.info["scoreWord"] = item.find("span", class_="review-ring-score__text").string
            self.info["subject"] = item.find("h4", class_="horizontal-card-item__title").string.replace("'", "\\\'")
            self.info["comment"] = ""
            self.info["url"] = url

            # 去详情页获取内容
            self.info["comment"] = self.parseDetail(self.info["url"]).replace("\'", "\\\'")
            # print(self.info)
            self.save(self.info)
            # exit(1)
        # 是否有下一页
        next_page = soup.find("ul", {"class": "paginate"}).find("li", class_="paginate__item skip next")
        if next_page:
            next_url = next_page.find("a").attrs["href"]
            return next_url
        else:
            return ""

    # 解析详情页获取评分及内容
    def parseDetail(self, url):
        content = ""
        data = self.http(url)
        soup = BeautifulSoup(data.text, "html.parser")

        # 正文
        main_info = soup.find("section", {"class": "article-body"})
        content_list = main_info.find_all("p")
        for p in content_list:

            content += p.get_text().replace("\'", "\\\'") + os.linesep
        # 优缺点
        breakdown = soup.find("div", class_="review-breakdown__inner")
        breakdown_good = breakdown.find("dl", class_="breakdown-good")

        for one in breakdown_good.children:
            if type(one) == bs4.element.NavigableString:
                content += one + os.linesep
            else:
                content += one.get_text() + os.linesep

        breakdown_bad = breakdown.find("dl", class_="breakdown-bad")
        for one in breakdown_bad.children:
            if type(one) == bs4.element.NavigableString:
                content += one + os.linesep
            else:
                content += one.get_text() + os.linesep
        # print(content)
        return content
