#!/usr/bin/python
# -*- coding:utf-8 -*-
from finder.ps4.hk import PS4Hk


def getFinder(area):
    # if str.lower(area) == "jp":
    #     return PS4Jp()
    # if str.lower(area) == "us":
    #     return PS4hUs()
    if str.lower(area) == "hk":
        return PS4Hk()
