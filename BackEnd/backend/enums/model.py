#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-08-10 17:49
# Author:  rongli
# Email:   abc@xyz.com
# File:    model.py
# Project: fa-demo
# IDE:     PyCharm

from enum import IntEnum


class UserGender(IntEnum):
    unknown = 0  # 未知
    male = 1  # 男
    female = 2  # 女


class MenuType(IntEnum):
    directory = 0   # 目录
    menu = 1    # 菜单
    button = 2  # 按钮
    link = 3    # 外链

