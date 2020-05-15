#!/usr/bin/python
# -*- coding:utf-8 -*-
from .hk import SwitchHk
from .jp import SwitchJp
from .us import SwitchUs
from .za import SwitchZa


def getFinder(area):
    if str.lower(area) == "jp":
        return SwitchJp()
    if str.lower(area) == "us":
        return SwitchUs()
    if str.lower(area) == "hk":
        return SwitchHk()
    if str.lower(area) == "za":
        return SwitchZa()
