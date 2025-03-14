# -*- coding: utf-8 -*-
# @Time    : 2023/3/24
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : ARC优化.py
# @Software: PyCharm
from collections import deque, defaultdict
from time import time


class _ARC:
    def __init__(self, capacity):
        self.capacity = capacity
        self.t1 = deque()
        self.t2 = deque()
        self.b1 = deque()
        self.b2 = deque()

        self.p = 0

        self.t1_lookup = set()
        self.t2_lookup = set()
        self.b1_lookup = set()
        self.b2_lookup = set()

    def _replace(self, key):
        if self.t1 and (len(self.t1) > self.p or (key in self.b2_lookup and len(self.t1) == self.p)):
            old_key = self.t1.pop()
            self.t1_lookup.remove(old_key)
            self.b1.appendleft(old_key)
            self.b1_lookup.add(old_key)
        else:
            old_key = self.t2.pop()
            self.t2_lookup.remove(old_key)
            self.b2.appendleft(old_key)
            self.b2_lookup.add(old_key)

        if len(self.b1) > self.capacity:
            self.b1.pop()
            self.b1_lookup.remove(old_key)
        if len(self.b2) > self.capacity:
            self.b2.pop()
            self.b2_lookup.remove(old_key)

    def get(self, key):
        if key in self.t1_lookup:
            self.t1.remove(key)
            self.t1_lookup.remove(key)
            self.t2.appendleft(key)
            self.t2_lookup.add(key)
            return True
        elif key in self.t2_lookup:
            self.t2.remove(key)
            self.t2.appendleft(key)
            return True
        elif key in self.b1_lookup:
            self._replace(key)
            self.b1.remove(key)
            self.b1_lookup.remove(key)
            self.t2.appendleft(key)
            self.t2_lookup.add(key)
            self.p = min(self.capacity, self.p + max(len(self.b2) // len(self.b1), 1))
            return False
        elif key in self.b2_lookup:
            self._replace(key)
            self.b2.remove(key)
            self.b2_lookup.remove(key)
            self.t2.appendleft(key)
            self.t2_lookup.add(key)
            self.p = max(0, self.p - max(len(self.b1) // len(self.b2), 1))
            return False
        else:
            return False

    def put(self, key):
        if not self.get(key):
            if len(self.t1) + len(self.b1) == self.capacity:
                if len(self.t1) < self.capacity:
                    self.b1.pop()
                    self.b1_lookup.remove(key)
                else:
                    self.t1.pop()
                    self.t1_lookup.remove(key)

            elif len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= self.capacity:
                if len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= 2 * self.capacity:
                    self.b2.pop()
                    self.b2_lookup.remove(key)

                self._replace(key)

            self.t1.appendleft(key)
            self.t1_lookup.add(key)


class ARC:
    def __init__(self, capacity, default_ttl=None):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.t1 = deque()
        self.t2 = deque()
        self.b1 = deque()
        self.b2 = deque()

        self.p = 0

        self.t1_lookup = dict()
        self.t2_lookup = dict()
        self.b1_lookup = set()
        self.b2_lookup = set()

        self.hits = 0
        self.misses = 0

    def _replace(self, key):
        if self.t1 and (len(self.t1) > self.p or (key in self.b2_lookup and len(self.t1) == self.p)):
            old_key = self.t1.pop()
            self.t1_lookup.pop(old_key)
            self.b1.appendleft(old_key)
            self.b1_lookup.add(old_key)
        else:
            old_key = self.t2.pop()
            self.t2_lookup.pop(old_key)
            self.b2.appendleft(old_key)
            self.b2_lookup.add(old_key)

        if len(self.b1) > self.capacity:
            self.b1.pop()
            self.b1_lookup.remove(old_key)
        if len(self.b2) > self.capacity:
            self.b2.pop()
            self.b2_lookup.remove(old_key)

    def get(self, key):
        if key in self.t1_lookup:
            value, ttl = self.t1_lookup[key]
            if self.default_ttl is not None and time() > ttl:
                self.t1.remove(key)
                self.t1_lookup.pop(key)
                return None

            self.hits += 1
            self.t1.remove(key)
            self.t1_lookup.pop(key)
            self.t2.appendleft(key)
            self.t2_lookup[key] = (value, ttl)
            return value
        elif key in self.t2_lookup:
            value, ttl = self.t2_lookup[key]
            if self.default_ttl is not None and time() > ttl:
                self.t2.remove(key)
                self.t2_lookup.pop(key)
                return None

            self.hits += 1
            self.t2.remove(key)
            self.t2.appendleft(key)
            return value
        else:
            self.misses += 1
            return None

    def put(self, key, value, ttl=None):
        if ttl is None:
            ttl = self.default_ttl
        if ttl is not None:
            ttl += time()

        if self.get(key) is not None:
            self.t2_lookup[key] = (value, ttl)
            return

        if len(self.t1) + len(self.b1) == self.capacity:
            if len(self.t1) < self.capacity:
                self.b1.pop()
                self.b1_lookup.remove(key)
            else:
                self.t1.pop()
                self.t1_lookup.pop(key)

        elif len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= self.capacity:
            if len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= 2 * self.capacity:
                self.b2.pop()
                self.b2_lookup.remove(key)

            self._replace(key)

        self.t1.appendleft(key)
        self.t1_lookup[key] = (value, ttl)

    def cache_hit_rate(self):
        return self.hits / (self.hits + self.misses) if self.hits + self.misses > 0 else 0


def main():
    a = ARC(3, 5)
    a.put("key1", 1)
    a.put("key2", 2)
    a.put("key3", 3)
    a.put("key4", 4)
    a.put("key5", 5)
    print(a.get("key1"))
    print(a.get("key2"))
    print(a.get("key3"))
    print(a.get("key4"))
# python代码实现 ARC算法，满足高效、可读、可扩展要求，采用最新技术实现。
# 在这个实现中，我们使用 `deque` 作为 LRU 和 LFU 队列的数据结构，并使用 `set` 来加速查找操作。`get` 方法用于从缓存中获取一个元素，如果元素存在，则返回 `True`，否则返回 `False`。`put` 方法用于向缓存中添加一个元素。
# 这个实现是高效的，因为它使用了合适的数据结构，同时它也是可读的，因为代码结构清晰。如果需要扩展这个实现，可以考虑添加元素过期时间、统计缓存命中率等功能。

# python代码实现 ARC算法，满足高效、可读、可扩展要求，采用最新技术实现。优化添加元素过期时间、统计缓存命中率等功能
# 这个实现在原有的ARC算法基础上，添加了以下功能：
#
#     支持设置元素的过期时间（TTL）。当获取元素时，会检查元素是否已过期，过期的元素将被移除。
#     统计缓存命中率。可以使用cache_hit_rate方法获取当前的缓存命中率。
# python ARC算法基础功能有哪些，除了优化添加元素过期时间、统计缓存命中率等功能，还有哪些功能可以添加呢？
# 您可以使用put方法添加元素，传入可选的TTL参数以设置元素的过期时间。使用get方法获取元素，如果元素不存在或已过期，将返回None。使用cache_hit_rate方法获取当前的缓存命中率。


if __name__ == '__main__':
    main()
