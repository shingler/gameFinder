# 从switch日服获取游戏数据并入库
import argparse

# curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = os.path.split(curPath)[0]
# sys.path.append(rootPath)

from finder import switch


def main():
    allowed_area = ["jp", "us", "za", "hk"]
    parser = argparse.ArgumentParser(description="请输入要指定的区域，目前仅支持[%s]" % ",".join(allowed_area))
    parser.add_argument('-a', '--area', default="hk", required=True, help="销售区域代码")
    parser.add_argument('-p', '--page', help="起始页数", default=0)

    args = parser.parse_args()

    if str.lower(args.area) not in allowed_area:
        print("销售区域代码填写有误")
        exit(0)
    area = str.lower(args.area)

    spider = switch.getFinder(area)
    size = 100
    page = spider.getPage(size)

    # 起始页数
    start = 1
    if int(args.page) > 0:
        start = int(args.page)

    for i in range(start, page+1):
        spider.getData(size, i)
        # break


if __name__ == "__main__":
    main()
    # print(int(time.mktime(time.strptime("2020.4.23", "%Y.%m.%d"))))