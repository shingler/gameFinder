# 抓取IGN的游戏评分
# http://www.ign.xn--fiqs8s/article/review?keyword__type=release
# http://www.ign.xn--fiqs8s/article/review?keyword__type=release&page=2&ist=broll
from bs4 import BeautifulSoup
from spider.spider import Spider


class Ign(Spider):
    def __init__(self):
        host = "http://www.ign.xn--fiqs8s"
        magazine = "IGN"
        super(Ign, self).__init__(host, magazine)

    # 分析内容并入库。如果没有内容则返回None
    def parse(self, content):
        # print(content.text)
        soup = BeautifulSoup(content.text, "html.parser")

        games = soup.find_all("article", {"class": "article REVIEW"})
        for item in games:
            msg = item.find("div", class_="m")
            # 评分
            score_soup = item.find("span", class_="side-wrapper side-wrapper hexagon-content")
            self.info["score"] = float(score_soup.string) if score_soup is not None else 0.0
            self.info["subject"] = msg.find("h3").find("a").string.replace("'", "\\\'")
            self.info["comment"] = msg.find("p").string.replace("'", "\\\'")
            self.info["url"] = msg.find("h3").find("a").attrs["href"]

            self.save(self.info)
            # break
