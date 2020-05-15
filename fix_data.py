#!/usr/bin/python
# -*- coding:utf-8 -*-
# 修复switch港服封图拼接错误
from finder import nsgame


def main():
    price_obj = nsgame.getFinder("switch", "hk")
    sql_select = "select id, cover from game_finder.subjects where saleArea='hk'"
    list1 = price_obj.query(sql_select)

    for item in list1:
        id = item["id"]
        cover = item["cover"]
        q = cover[len("https://www.nintendo.com.hk"):]
        new_cover = "https://www.nintendo.com.hk/software/img/bnr/%s" % q
        # print(new_cover)
        # exit(1)
        sql_update = "update game_finder.subjects set cover='%s' where id=%d" % (new_cover, id)
        # print(sql_update)
        # exit(1)
        price_obj.write(sql_update)


if __name__ == "__main__":
    main()