#!/usr/bin/python
# -*- coding:utf-8 -*-
from spider.famitsu import Famitsu
import argparse
import sys, time
from spider.ign import Ign
from spider.gamespot import Gamespot
from spider.metacritic import Metacritic


# 爬取法米通的评测
def get_famitsu(page=1):
    fa = Famitsu()
    retry = 0
    url = "%s/schedule/recent/all/%d/" % (fa.host, page)

    while True:
        try:
            data = Famitsu.http(url)
        except Exception as ex:
            print(ex)
            if retry < 3:
                retry += 1
                print("访问超时%d" % retry)
                continue
            else:
                print("访问超时，脚本中止")
                sys.exit(1)

        next_uri = fa.parse(data)
        if len(next_uri) > 0:
            url = "%s%s" % (fa.host, next_uri)
            print(url)
            time.sleep(1)
            # break
        else:
            break


# 爬取IGN的评测（IGN中国已死，国际站无法访问，放弃）
def get_ign(page=1):
    ign = Ign()
    retry = 0
    while True:
        url = "http://www.ign.xn--fiqs8s/article/review?keyword__type=release&page=%d&ist=broll" % page
        try:
            data = Ign.http(url)
        except:
            print("访问超时%d" % retry)
            if retry < 3:
                retry += 1
                continue
        # 404了，没有数据了就中止
        if data is None:
            break

        ign.parse(data)
        page += 1

    print("数据已抓取完毕")


# 爬取GameSpot
def get_gamespot(page=1):
    gs = Gamespot()
    url = "%s/games/reviews/?page=%s" % (gs.host, page)
    retry = 0
    while True:
        try:
            data = gs.http(url)
        except:
            print("访问超时%d" % retry)
            if retry < 3:
                retry += 1
                continue
        else:
            next_uri = gs.parse(data)
            if len(next_uri) > 0:
                url = "%s%s" % (gs.host, next_uri)
                print(url)
                time.sleep(1)
                # break
            else:
                break


# 爬取metacritics
def get_metacritic(page=0):
    metacritic = Metacritic()
    url = "%s/browse/games/score/metascore/all/all/filtered?sort=desc" % metacritic.host
    if int(page) > 1:
        url += "&page="+page
    retry = 0
    while True:
        try:
            data = metacritic.http(url)
        except Exception as ex:
            print(ex)
            print("访问超时%d" % retry)
            if retry < 3:
                retry += 1
                continue
        else:
            next_uri = metacritic.parse(data)
            if len(next_uri) > 0:
                url = "%s%s" % (metacritic.host, next_uri)
                print(url)
                time.sleep(1)
                # break
            else:
                break


def main():
    allowed_magazine = ['famitsu', 'gamespot', 'metacritic']
    parser = argparse.ArgumentParser(description="需要指定哪个媒体[%s]" % ','.join(allowed_magazine))
    parser.add_argument('-n', '--name', help="媒体名称", required=True)
    parser.add_argument('-p', '--page', help="起始列表页数", default=1)
    args = parser.parse_args()

    # print(args.magazine)

    if str.lower(args.name) in allowed_magazine:
        eval("get_"+args.name)(int(args.page))
    else:
        print("运行参数错误，-n的值只能是[%s]" % ','.join(allowed_magazine))


if __name__ == "__main__":
    main()