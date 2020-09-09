# 从switch美服获取游戏数据并入库
import time
import urllib

import requests
import json

from finder import nsgame
from bs4 import BeautifulSoup

from finder.store import Store


class SwitchUs(Store):
    currency = "USD"
    saleArea = "US"
    url = "https://www.nintendo.com%s"
    price_url = "https://api.ec.nintendo.com/v1/price?country=US&lang=zh&ids=%s"

    # 获取游戏总数
    def getCount(self, method="get", data=None, format="json"):
        data = '{"requests":[{"indexName":"noa_aem_game_en_us","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=1&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22platform%3ANintendo%20Switch%22%5D%5D"},{"indexName":"noa_aem_game_en_us","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=platform"}]}'
        json_data = super(SwitchUs, self).getCount("post", data=data)

        # 总数
        block = json_data["results"][1]["facets"]["platform"]
        total = int(block["Nintendo Switch"])

        return total

    def getPageData(self, size=1, page=1) -> list:
        print(size, page)
        url = self.list_url
         # 所有switch游戏，有效的，按发售日排序
        data = '{"requests":[{"indexName":"noa_aem_game_en_us_release_des","params":"query=&hitsPerPage={0}&maxValuesPerFacet=100&page={1}&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22availability%3AAvailable%20now%22%5D%2C%5B%22platform%3ANintendo%20Switch%22%5D%5D"},{"indexName":"noa_aem_game_en_us_release_des","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availability&facetFilters=%5B%5B%22platform%3ANintendo%20Switch%22%5D%5D"},{"indexName":"noa_aem_game_en_us_release_des","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=platform&facetFilters=%5B%5B%22availability%3AAvailable%20now%22%5D%5D"}]}'
        # 需要单独替换param，整体替换会报错说找不到requests，我怀疑里面大括号太多了！
        list = json.loads(data)
        param = urllib.parse.unquote(list["requests"][0]["params"])
        list["requests"][0]["params"] = param.format(size, page)
        data = json.dumps(list)
        print(data)

        resp = requests.post(url, data=data, headers=self.headers, allow_redirects=False)
        data_list = json.loads(resp.text, encoding="UTF-8")
        print(data_list)
        return data_list["results"][0]["hits"]

    def saveData(self, data, for_test=False) -> int:
        if "nsuid" not in data:
            return 0

        # 游戏资料
        officialGameId = data["nsuid"]

        # 游戏价格
        price_obj = nsgame.getFinder(platform="switch", area=str.lower(self.saleArea))

        # 是否存在。如果存在就不爬详情页了，节约时间
        exist = price_obj.getDataByOfficeGameId(officialGameId)

        price_obj.officialGameId = "fake_" + officialGameId if for_test else officialGameId
        price_obj.subject = data["title"].replace("'", "\\\'")
        price_obj.intro = data["description"].replace("'", "\\\'")
        if "boxArt" in data:
            price_obj.cover = "https://www.nintendo.com/%s" % data["boxArt"]
        price_obj.video = ""
        # 未发售游戏的发售日无法转换
        price_obj.publishDateStr = data["releaseDateMask"]
        if "T" in data["releaseDateMask"]:
            date_str = data["releaseDateMask"][:data["releaseDateMask"].rfind("T")]
            try:
                price_obj.publishDate = int(time.mktime(time.strptime(date_str, "%Y-%m-%d")))
            except:
                pass

        price_obj.players = data["players"]
        price_obj.platform = "switch"
        price_obj.edition = ""
        # 没有发售日期的游戏没有价格
        price_obj.price = data["msrp"] if ("msrp" in data) and (data["msrp"] == 'None') else -1

        price_obj.url = self.url % data["url"]
        price_obj.rate = "ESRB : %s" % data["esrb"]

        # 获取价格
        self.getSalePrice(price_obj, officialGameId)

        price_obj.historyPrice = price_obj.latestPrice  # 保存的时候会检查
        price_obj.hisDate = int(time.time())
        price_obj.created = int(time.time())
        price_obj.updated = int(time.time())

        if exist is None:
            self.getDetail(price_obj, price_obj.url)

        print("%s saved." % price_obj.subject)
        return price_obj.save()

    # 进入详情页，获取更新信息
    def getDetail(self, price_obj, url):
        resp = requests.get(url, headers=self.headers, allow_redirects=False)
        soup = BeautifulSoup(resp.text, "html.parser")
        # 获取截图
        thumb_li = soup.find_all("product-gallery-item")
        price_obj.thumb = []
        for li in thumb_li:
            if li.attrs["type"] == "image":
                price_obj.thumb.append(self.url % li.attrs["src"])
        price_obj.thumb = json.dumps(price_obj.thumb)
        # 支持语言
        try:
            overview = soup.find("section", id="overview")
            price_obj.edition = overview.find("dd", class_="languages").text.strip()
        except:
            print(url, overview)

    # 获取折扣价及日期
    def getSalePrice(self, price_obj, officalGameId):
        sale_url = self.price_url % officalGameId
        resp = requests.get(sale_url, headers=self.headers)
        data_list = json.loads(resp.text, encoding="UTF-8")
        if "discount_price" in data_list["prices"]:
            price_obj.latestPrice = data_list["prices"]["discount_price"]["raw_value"]
            price_obj.latestExpire = int(time.mktime(time.strptime(data_list["prices"]["discount_price"]["end_datetime"], "%Y-%m-%dT%H:%M:%SZ")))


