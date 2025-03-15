# -*- coding: utf-8 -*-
# @Time    : 2023/5/20
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : doorkeeper.py
# @Software: PyCharm
from probables import BloomFilter


class Doorkeeper:
    def __init__(self, cap=100000, false_positive=0.01):
        self.bloom = BloomFilter(cap, false_positive)

    def __insert(self, key: str):
        already_present = self.bloom.check(key)
        self.bloom.add(key)
        return already_present

    def allow(self, key: str):
        return self.__insert(key)

    def reset(self):
        self.bloom.clear()