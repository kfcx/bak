# -*- coding: utf-8 -*-
# @Time    : 2023/3/24
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : 实现.py
# @Software: PyCharm
import collections


class FastARC:
    def __init__(self, capacity):
        self.capacity = capacity
        self.p = 0
        self.cache = set()
        self.t1 = collections.deque()
        self.t2 = collections.deque()
        self.b1 = collections.deque()
        self.b2 = collections.deque()

    def _replace(self, key):
        if len(self.t1) > 0 and (len(self.t2) == 0 or key in self.b2):
            old_key = self.t1.popleft()
            self.b1.append(old_key)
        else:
            old_key = self.t2.popleft()
            self.b2.append(old_key)
        self.cache.remove(old_key)

    def get(self, key):
        if key in self.cache:
            if key in self.t1:
                self.t1.remove(key)
            else:
                self.t2.remove(key)
            self.t2.append(key)
            return True
        return False

    def put(self, key):
        if key in self.cache:
            self.get(key)
            return

        if len(self.t1) + len(self.b1) == self.capacity:
            if len(self.t1) < self.capacity:
                self.b1.popleft()
            else:
                old_key = self.t1.popleft()
                self.cache.remove(old_key)

        if key in self.b1:
            self.p = min(self.capacity, self.p + max(len(self.b2) // len(self.b1), 1))
            self._replace(key)
        elif key in self.b2:
            self.p = max(0, self.p - max(len(self.b1) // len(self.b2), 1))
            self._replace(key)
        else:
            if len(self.cache) >= self.capacity:
                self._replace(key)

        if key in self.b1:
            self.b1.remove(key)
        elif key in self.b2:
            self.b2.remove(key)

        self.t1.append(key)
        self.cache.add(key)


def main():
    # Usage example:
    cache = FastARC(3)
    cache.put(1)
    cache.put(2)
    cache.put(3)
    print(cache.get(1))  # Returns False, as item 1 was replaced
    print(cache.get(2))  # Returns True, as item 2 is in the cache
    cache.put(4)  # Replaces the least recently used item
    cache.put(5)  # Replaces the least recently used item
    print(cache.cache)


if __name__ == '__main__':
    main()
