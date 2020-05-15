# 抓取metacritic的评分
# https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?sort=desc
import os, time
from bs4 import BeautifulSoup, SoupStrainer
from spider.spider import Spider


class Metacritic(Spider):
    platform = ["PS4", "Switch"]

    def __init__(self):
        host = "https://www.metacritic.com"
        magazine = "metacritic"
        super(Metacritic, self).__init__(host, magazine)

    # 解析列表，抓取评分，标题
    def parse(self, content):
        soup = BeautifulSoup(content.text, "html.parser")

        games = soup.select("li.game_product")
        for item in games:
            title_soup = item.find("div", class_="basic_stat product_title").find("a")
            url = self.host + title_soup.attrs["href"]
            # 如果已入库就不重复获取详情了
            if bool(self.ifExists(url)):
                continue

            # 获取平台信息，只抓取指定平台数据
            subject = title_soup.string.strip().replace("'", "\\\'")
            plat_str = subject[subject.find('(')+1:subject.find(')')]
            if plat_str not in self.platform:
                continue

            self.info["score"] = float(item.find("div", class_="basic_stat product_score brief_metascore").contents[1].string)
            self.info["subject"] = subject[:subject.find('(')]
            self.info["url"] = url
            self.info["comment"] = ""

            # 获取评价内容
            comment = self.parseDetail(url)
            self.info["comment"] = comment.replace("\'", "\\\'").strip()
            # print(self.info)
            res = self.save(self.info)
            # exit(1)
        # 是否有下一页
        next_page = soup.find("div", {"class": "page_nav"}).find("span", class_="flipper next")
        if next_page.find("a"):
            next_url = next_page.find("a").attrs["href"]
            return next_url
        else:
            return ""

    # 解析详情页获取评分及内容
    def parseDetail(self, url):
        content = ""
        url += "/critic-reviews"
        try:
            data = self.http(url)
        except Exception as e:
            print(e.with_traceback())
            time.sleep(1)
            return ""
        else:
            only_tag = SoupStrainer("ol", class_="reviews critic_reviews")
            soup = BeautifulSoup(data.text, "html.parser", parse_only=only_tag)
            reviews = soup.find_all("div", class_="review_body")

            for r in reviews:
                # print(r, type(r))
                content += r.string + os.linesep

            # print(content)
            return content
