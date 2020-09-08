# switch游戏爬虫测试用例，可作为测试用例的基类
import random
import unittest

from finder import switch, nsgame
from finder.base import Platform


class SwitchScrapeTestCase(unittest.TestCase):
    sale_area_name = "香港"
    sale_area = "HK"
    list_url = ""
    data_list = []
    saved_id = 0

    @classmethod
    def start(cls) -> None:
        print("switch%s游戏爬虫测试用例" % cls.sale_area_name)

    @classmethod
    def cleanup(cls) -> None:
        if cls.saved_id != 0:
            print("删除测试数据，id=%s" % cls.saved_id)
            ns_obj = nsgame.getFinder("switch", cls.sale_area)
            ns_obj.delete(cls.saved_id)

    # 1.获取列表地址模板
    def store_url(self):
        print("1：获取%s列表url模板" % self.__class__.sale_area_name)
        platform_obj = Platform()
        platform_data = platform_obj.get(platform="switch", area=self.__class__.sale_area.upper())
        self.assertNotEqual("", platform_data["url"], "列表页模板为空")
        self.assertNotEqual("", platform_data["countryArea"], "销售代码为空")
        self.__class__.list_url = platform_data["url"]
        self.__class__.sale_area = platform_data["countryArea"]

    # 2.获取总数
    def list_count_can_scrape(self):
        # print(self.__class__.list_url)
        print("2：测试能否获得列表总数")
        ns_obj = switch.getFinder(self.__class__.sale_area)
        count = ns_obj.getCount()
        self.assertNotEqual(0, count)
        print("游戏总数=%d" % count)

    # 3.解析第一页游戏
    def page_data_can_scrape(self):
        print("3：测试第一页数据能否获取")
        ns_obj = switch.getFinder(self.__class__.sale_area)
        data_list = ns_obj.getPageData(size=30, page=1)
        self.assertNotEqual(0, len(data_list), "游戏列表为空")
        self.__class__.data_list = data_list

    # 4.保存第一页随机一个游戏（fake前缀）
    def one_game_can_scrape(self):
        print("4：测试第一页随机一个游戏能否保存入库")
        data_list = self.__class__.data_list
        one = random.choice(data_list)
        ns_obj = switch.getFinder(self.__class__.sale_area)
        saved_id = ns_obj.saveData(one, for_test=True)
        self.assertNotEqual(0, saved_id, "保存失败")
        self.__class__.saved_id = saved_id

    # 5.确认已保存的游戏数据正确性
    def data_is_saved(self):
        print("5：测试抓取的数据是否已正常入库")
        ns_obj = nsgame.getFinder("switch", self.__class__.sale_area)
        one = ns_obj.getDataById(self.__class__.saved_id)
        self.assertIsNotNone(one, "数据不存在")
        self.assertIsNotNone(one["officialGameId"], "游戏官方ID为空")
        self.assertIsNotNone(one["subject"], "标题不能为空")
        self.assertNotEqual(0, one["price"], "游戏价格为0")
        print(one)
