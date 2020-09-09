# switch港服游戏爬虫测试用例
import unittest
from tests.scrape_ns_game_test import SwitchScrapeTestCase


class SwitchUsScrapeTestCase(SwitchScrapeTestCase):
    sale_area_name = "美国"
    sale_area = "US"

    @classmethod
    def setUpClass(cls) -> None:
        cls.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.cleanup()

    def test_1_store_url(self):
        super(self.__class__, self).store_url()

    def test_2_list_count_can_scrape(self):
        super(self.__class__, self).list_count_can_scrape()

    def test_3_page_data_can_scrape(self):
        super(self.__class__, self).page_data_can_scrape()

    def test_4_one_game_can_scrape(self):
        super(self.__class__, self).one_game_can_scrape()

    def test_5_data_is_saved(self):
        super(self.__class__, self).data_is_saved()


if __name__ == '__main__':
    unittest.main()
