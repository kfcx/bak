# -*- coding: utf-8 -*-
# @Author  : Naihe
# @File    : arc测试.py
import collections


class FastARC:
    def __init__(self, cache_size):
        self.cache_size = cache_size
        self.p = 0
        self.cache = collections.OrderedDict()
        self.t1 = collections.OrderedDict()
        self.t2 = collections.OrderedDict()
        self.b1 = collections.OrderedDict()
        self.b2 = collections.OrderedDict()

    def access(self, item):
        if item in self.t1 or item in self.t2:
            self.cache_hit(item)
        else:
            self.cache_miss(item)

    def cache_hit(self, item):
        if item in self.t1:
            self.t1.pop(item)
        else:
            self.t2.pop(item)
        self.t2[item] = None

    def cache_miss(self, item):
        if len(self.t1) + len(self.b1) == self.cache_size:
            if len(self.t1) < self.cache_size:
                self.b1.popitem(last=False)
                self.replace()
            else:
                self.t1.popitem(last=False)
        elif len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= self.cache_size:
            if len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= 2 * self.cache_size:
                self.b2.popitem(last=False)
            self.replace()

        if item in self.b1:
            self.p = min(self.p + max(len(self.b2) // len(self.b1), 1), self.cache_size)
            self.b1.pop(item)
        elif item in self.b2:
            self.p = max(self.p - max(len(self.b1) // len(self.b2), 1), 0)
            self.b2.pop(item)
        else:
            self.cache[item] = None

        self.t1[item] = None

    def replace(self):
        if len(self.t1) > 0 and (len(self.t1) > self.p or (len(self.t1) == self.p and len(self.b2) == 0)):
            old_item = self.t1.popitem(last=False)
            self.b1[old_item[0]] = None
        else:
            old_item = self.t2.popitem(last=False)
            self.b2[old_item[0]] = None


def main():
    pass


if __name__ == '__main__':
    main()
