# 从ps港服获取游戏数据并入库
import argparse

from finder import ps4


def main():
    allowed_area = ["hk"]
    parser = argparse.ArgumentParser(description="抓取PS4游戏价格信息，可选的区域有[%s]" % ','.join(allowed_area))
    parser.add_argument('-a', '--area', default="hk", required=True, help="商店销售区域代码")
    parser.add_argument('-p', '--page', default=1, help="开始页数")
    args = parser.parse_args()
    area = args.area
    start_page = int(args.page)

    spider = ps4.getFinder(area)
    size = 100
    page = spider.getPage(size)

    for i in range(start_page, page + 1):
        spider.getData(size, i)
        # break


if __name__ == "__main__":
    main()
