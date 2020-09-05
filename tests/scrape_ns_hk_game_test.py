# switch港服游戏爬虫测试用例
import random
import unittest

from finder import switch, nsgame
from finder.base import Platform


class SwitchHkScrapeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("switch港服游戏爬虫测试用例")
        globals()["list_url"] = ""
        globals()["sale_area"] = ""
        globals()["data_list"] = []
        globals()["saved_id"] = 0

    @classmethod
    def tearDownClass(cls) -> None:
        if globals()["saved_id"] != 0:
            print("删除测试数据，id=%s" % globals()["saved_id"])
            ns_obj = nsgame.getFinder("switch", globals()["sale_area"])
            ns_obj.delete(globals()["saved_id"])

    # 1.获取列表地址模板
    def test_1_store_url(self):
        print("1：获取港服列表url模板")
        platform_obj = Platform()
        platform_hk = platform_obj.get(platform="switch", area="HK")
        self.assertNotEqual("", platform_hk["url"], "列表页模板为空")
        self.assertNotEqual("", platform_hk["countryArea"], "销售代码为空")
        globals()["list_url"] = platform_hk["url"]
        globals()["sale_area"] = platform_hk["countryArea"]

    # 2.获取总数
    def test_2_list_count_can_scrape(self):
        print("2：测试能否获得列表总数")
        ns_obj = switch.getFinder(globals()["sale_area"])
        count = ns_obj.getCount()
        self.assertNotEqual(0, count)
        print("游戏总数=%d" % count)

    # 3.解析第一页游戏
    def test_3_page_data_can_scrape(self):
        print("3：测试第一页数据能否获取")
        ns_obj = switch.getFinder(globals()["sale_area"])
        data_list = ns_obj.getPageData(size=30, page=1)
        self.assertNotEqual(0, len(data_list), "游戏列表为空")
        globals()["data_list"] = data_list

    # 4.保存第一页随机一个游戏（fake前缀）
    def test_4_one_game_can_scrape(self):
        print("4：测试第一页随机一个游戏能否保存入库")
        data_list = globals()["data_list"]
        one = random.choice(data_list)
        ns_obj = switch.getFinder(globals()["sale_area"])
        saved_id = ns_obj.saveData(one, for_test=True)
        self.assertNotEqual(0, saved_id, "保存失败")
        globals()["saved_id"] = saved_id

    # 5.确认已保存的游戏数据正确性
    def test_5_data_is_saved(self):
        print("5：测试抓取的数据是否已正常入库")
        ns_obj = nsgame.getFinder("switch", globals()["sale_area"])
        one = ns_obj.getDataById(globals()["saved_id"])
        self.assertIsNotNone(one, "数据不存在")
        self.assertIsNotNone(one["officialGameId"], "游戏官方ID为空")
        self.assertIsNotNone(one["subject"], "标题不能为空")
        self.assertNotEqual(0, one["price"], "游戏价格为0")
        print(one)


if __name__ == '__main__':
    unittest.main()
