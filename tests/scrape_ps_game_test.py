# ps4港服游戏爬虫测试用例
import random
import unittest

import finder
from finder import ps4, ps4game
from finder.base import Platform


class Playstation4GameTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        print("ps4港服游戏爬虫测试用例")
        globals()["list_url"] = ""
        globals()["sale_area"] = ""
        globals()["data_list"] = {}
        globals()["saved_id"] = 0

    # 获取港服列表url模板
    def test_1_store_url(self) -> None:
        print("1：获取港服列表url模板")
        platform_obj = Platform()
        platform_ps4_hk = platform_obj.get(platform="PS4", area="HK")
        self.assertNotEqual("", platform_ps4_hk["url"], "列表页模板为空")
        self.assertNotEqual("", platform_ps4_hk["countryArea"], "销售代码为空")
        globals()["list_url"] = platform_ps4_hk["url"]
        globals()["sale_area"] = platform_ps4_hk["countryArea"]

    # 测试能否获得列表总数
    def test_2_list_count_can_scrape(self):
        print("2：测试能否获得列表总数")
        ps4Game = ps4.getFinder("hk")
        count = ps4Game.getCount()
        self.assertNotEqual(0, count, "列表页总数不能为0")
        self.assertIsNotNone(count, msg="列表页总数不能为None")
        print("总数为%d" % count)

    # 测试第一页数据能否获取
    def test_3_page_data_can_scrape(self):
        print("3：测试第一页数据能否获取")
        ps4Game = ps4.getFinder("hk")
        size = 30
        page1_list = ps4Game.getPageData(size=size, page=1)
        data_list = []
        for data in page1_list["included"]:
            # 游戏资料
            if data["type"] == "game":
                data_list.append(data)
        self.assertNotEqual(0, len(data_list), "游戏列表第一页数据总数为0")
        globals()["data_list"] = data_list

    # 测试第一页随机一个游戏能否保存入库
    def test_4_one_game_can_scrape(self):
        print("4：测试第一页随机一个游戏能否保存入库")
        data_list = globals()["data_list"]
        one = random.choice(data_list)
        # 给官方id前加前缀fake防止重复写入
        one["id"] = "fake_" + one["id"]
        print("随机写入的游戏官方ID是%s，名字是%s" % (one["id"], one["attributes"]["name"].replace("'", "\\\'")))
        ps4Game = ps4.getFinder("hk")
        price_id = ps4Game.storeData(one)
        self.assertNotEqual(0, price_id, "写入失败")
        print("写入的数据id=%s" % price_id)
        globals()["saved_id"] = price_id

    # 测试抓取的数据是否已正常入库
    def test_5_data_is_saved(self):
        print("5：测试抓取的数据是否已正常入库")
        price_id = globals()["saved_id"]
        game_obj = ps4game.getFinder("ps4", globals()["sale_area"])
        self.assertIsInstance(game_obj, finder.base.Price, "对象类型不对")
        data = game_obj.getDataById(price_id)
        self.assertIsNotNone(data, "数据不存在")
        self.assertIsNotNone(data["officialGameId"], "游戏官方ID为空")
        self.assertIsNotNone(data["subject"], "标题不能为空")
        self.assertNotEqual(0, data["price"], "游戏价格为0")
        print(data)

    @classmethod
    def tearDownClass(self):
        if globals()["saved_id"] != 0:
            print("删除测试数据，id=%s" % globals()["saved_id"])
            game_obj = ps4game.getFinder("ps4", globals()["sale_area"])
            game_obj.delete(globals()["saved_id"])


if __name__ == '__main__':
    unittest.main()
