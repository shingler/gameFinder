# 从switch美服获取游戏数据并入库
import time
import urllib

import requests
import json

from finder import nsgame
from bs4 import BeautifulSoup

from finder.store import Store


class SwitchUs(Store):

    def __init__(self):
        super(SwitchUs, self).__init__()
        self.currency = "USD"
        self.saleArea = "US"
        self.url = "https://www.nintendo.com%s"
        self.count_url = "https://u3b6gr4ua3-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.22.1%3BJS%20Helper%202.20.1&x-algolia-application-id=U3B6GR4UA3&x-algolia-api-key=9a20c93440cf63cf1a7008d75f7438bf"

    # 获取游戏总数
    def getCount(self):
        data = '{"requests":[{"indexName":"noa_aem_game_en_us","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=1&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22platform%3ANintendo%20Switch%22%5D%5D"},{"indexName":"noa_aem_game_en_us","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=platform"}]}'
        json_data = super(SwitchUs, self).getCount("post", data=data)

        # 总数
        block = json_data["results"][1]["facets"]["platform"]
        total = int(block["Nintendo Switch"])

        return total

    # 获取游戏资料
    def getData(self, size=1, page=1):
        print(size, page)
        # url = "https://u3b6gr4ua3-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.22.1%3BJS%20Helper%202.20.1&x-algolia-application-id=U3B6GR4UA3&x-algolia-api-key=9a20c93440cf63cf1a7008d75f7438bf"
        url = "https://u3b6gr4ua3-2.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%20(lite)%3B%20JS%20Helper%202.20.1&x-algolia-application-id=U3B6GR4UA3&x-algolia-api-key=9a20c93440cf63cf1a7008d75f7438bf"
        # data = '{"requests":[{"indexName":"noa_aem_game_en_us","params":"query=&hitsPerPage={0}&maxValuesPerFacet=30&page={1}&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22platform%3ANintendo%20Switch%22%5D%5D"},{"indexName":"noa_aem_game_en_us","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=platform"}]}'
        # 所有switch游戏，有效的，按发售日排序
        data = '{"requests":[{"indexName":"noa_aem_game_en_us_release_des","params":"query=&hitsPerPage={0}&maxValuesPerFacet=100&page={1}&facets=%5B%22generalFilters%22%2C%22platform%22%2C%22availability%22%2C%22categories%22%2C%22filterShops%22%2C%22virtualConsole%22%2C%22characters%22%2C%22priceRange%22%2C%22esrb%22%2C%22filterPlayers%22%5D&tagFilters=&facetFilters=%5B%5B%22availability%3AAvailable%20now%22%5D%2C%5B%22platform%3ANintendo%20Switch%22%5D%5D"},{"indexName":"noa_aem_game_en_us_release_des","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availability&facetFilters=%5B%5B%22platform%3ANintendo%20Switch%22%5D%5D"},{"indexName":"noa_aem_game_en_us_release_des","params":"query=&hitsPerPage=1&maxValuesPerFacet=30&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=platform&facetFilters=%5B%5B%22availability%3AAvailable%20now%22%5D%5D"}]}'
        # 需要单独替换param，整体替换会报错说找不到requests，我怀疑里面大括号太多了！
        list = json.loads(data)
        param = urllib.parse.unquote(list["requests"][0]["params"])
        list["requests"][0]["params"] = param.format(size, page)
        data = json.dumps(list)
        print(data)

        resp = requests.post(url, data=data, headers=self.headers)
        data_list = json.loads(resp.text, encoding="UTF-8")
        print(data_list)

        # 美服使用algolia做分页。由于缺少索引控制，只能获取1000条数据。只能等后续他们更新了，哎
        if len(data_list["results"][0]["hits"]) > 0:
            for data in data_list["results"][0]["hits"]:
                if "nsuid" not in data:
                    continue

                # 游戏资料
                officialGameId = data["nsuid"]

                # 游戏价格
                price_obj = nsgame.getFinder(platform="switch", area=str.lower(self.saleArea))

                # 是否存在。如果存在就不爬详情页了，节约时间
                exist = price_obj.getDataByOfficeGameId(officialGameId)

                price_obj.officialGameId = officialGameId
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
                self.getSalePrice(price_obj, price_obj.officialGameId)

                price_obj.historyPrice = price_obj.latestPrice # 保存的时候会检查
                price_obj.hisDate = int(time.time())
                price_obj.created = int(time.time())
                price_obj.updated = int(time.time())

                if exist is None:
                    self.getDetail(price_obj, price_obj.url)

                price_obj.save()
                print("%s saved." % price_obj.subject)
            # break

    # 进入详情页，获取更新信息
    def getDetail(self, price_obj, url):
        resp = requests.get(url, headers=self.headers)
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
        resp = requests.get("https://api.ec.nintendo.com/v1/price?country=US&lang=zh&ids=%s" % officalGameId, headers=self.headers)
        data_list = json.loads(resp.text, encoding="UTF-8")
        if "discount_price" in data_list["prices"]:
            price_obj.latestPrice = data_list["prices"]["discount_price"]["raw_value"]
            price_obj.latestExpire = int(time.mktime(time.strptime(data_list["prices"]["discount_price"]["end_datetime"], "%Y-%m-%dT%H:%M:%SZ")))


