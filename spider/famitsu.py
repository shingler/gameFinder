# 抓取fami通的游戏评分
# 和其他杂志不同，fami通的入口较深，需要从发售日期栏目，找到已发售页面
# 获取url之后，进入详情页抓取评分
from bs4 import BeautifulSoup

from spider.spider import Spider


class Famitsu(Spider):
    platform = ['switch', 'ps4']
    def __init__(self):
        host = "https://www.famitsu.com"
        magazine = "Famitsu"
        super(Famitsu, self).__init__(host, magazine)

    # 分析内容并入库。如果没有内容则返回None
    def parse(self, content):
        # print(content.text)
        soup = BeautifulSoup(content.text, "html.parser")

        games = soup.find_all("div", {"class": "card-schedule"})
        for item in games:
            msg = item.find("a", class_="card-schedule__inner")
            # 只抓取指定平台的游戏
            console = msg.find("span", class_="icon-console").text
            if str.lower(console) in self.platform:
                self.info["subject"] = msg.find("span", class_="card-schedule__title-inline").text.replace("'", "\\\'")
                url = self.host + msg.attrs["href"]
                # 如果已入库就不重复获取详情了
                if bool(self.ifExists(url)):
                    continue

                self.info["url"] = url
                # 进入详情页
                detail = Spider.http(self.info["url"])
                if detail is not None:
                    self.info["score"], self.info["comment"] = self.parseDetail(detail)
                    # print(self.info)
                    self.info["comment"] = self.info["comment"].replace("\'", "\\\'")
                    # 有分数再入库吧，好多没分或者重复的
                    if self.info["score"] > 0:
                        self.save(self.info)
            # break

        # 是否有下一页
        next_page = soup.find("li", class_="ft-pager__item ft-pager__item--next")

        if next_page:
            next_url = next_page.find("a").attrs["href"]
            return next_url
        else:
            return ""

    # 解析详情页获取评分
    def parseDetail(self, data):
        soup = BeautifulSoup(data.text, "html.parser")
        # print(data.text)
        info = soup.find("div", {"class": "game-title-info"})
        # print(info)
        score_bar = info.find("div", class_="game-title-info__cross-review").find("div", class_="progress__percent")
        # print(score_bar)
        # 如果没有评分
        score_int = score_bar.find("span", class_="int").text if score_bar.find("span", class_="int") else "0"
        score_dec = score_bar.find("span", class_="dec").text if score_bar.find("span", class_="dec") else "0"
        score = float("%s%s" % (score_int, score_dec))
        comment = info.find("div", class_="game-title-info__overview").text if info.find("div", class_="game-title-info__overview") else "empty"
        return score, comment
