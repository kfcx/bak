# -*- coding: utf-8 -*-
# @Time    : 2023/3/26
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : base.py
# @Software: PyCharm

import threading
import time
from collections import defaultdict, deque
from typing import Callable, Optional, Union


class CacheNode:
    def __init__(self, key, value, expiry_time):
        self.key = key
        self.value = value
        self.expiry_time = expiry_time


class ARC:
    def __init__(self, capacity: int, eviction_policy: str = "ARC", default_ttl: Optional[float] = None):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.eviction_policy = eviction_policy.lower()
        self.cache = {}
        self.t1 = deque()  # Top cache
        self.t2 = deque()  # Bottom cache
        self.b1 = deque()  # Ghost list for recently evicted items from T1
        self.b2 = deque()  # Ghost list for recently evicted items from T2
        self.p = 0  # Adaptation parameter
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
        self.timer = threading.Timer(1, self.expire_keys)
        self.timer.start()

    def expire_keys(self):
        with self.lock:
            for key, node in list(self.cache.items()):
                if node.expiry_time and node.expiry_time < time.time():
                    self.delete(key)
        self.timer = threading.Timer(1, self.expire_keys)
        self.timer.start()

    def _replace(self, key):
        if len(self.t1) >= max(1, self.p) and key in self.b2:
            old_key = self.t1.popleft()
            self.b1.append(old_key)
            del self.cache[old_key]
        else:
            old_key = self.t2.popleft()
            self.b2.append(old_key)
            del self.cache[old_key]

    def _move_to_top(self, node: CacheNode):
        self.t2.remove(node.key)
        self.t1.append(node.key)

    def set_eviction_policy(self, policy: str):
        self.eviction_policy = policy.lower()

    def resize(self, new_capacity: int):
        with self.lock:
            self.capacity = new_capacity
            while len(self.cache) > self.capacity:
                if self.eviction_policy == "lru":
                    self.t1.popleft()
                elif self.eviction_policy == "lfu":
                    self.t2.popleft()
                elif self.eviction_policy == "arc":
                    self._replace(None)
                else:
                    raise ValueError(f"Unknown eviction policy: {self.eviction_policy}")

    def get(self, key, default=None):
        with self.lock:
            node = self.cache.get(key)
            if node is None:
                self.misses += 1
                return default
            if node.expiry_time and node.expiry_time < time.time():
                self.delete(key)
                self.misses += 1
                return default
            self.hits += 1
            if key in self.t1:
                self._move_to_top(node)
            return node.value

    def put(self, key, value, ttl: Optional[float] = None):
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.value = value
                if ttl is not None:
                    node.expiry_time = time.time() + ttl
                elif self.default_ttl is not None:
                    node.expiry_time = time.time() + self.default_ttl
                return
            expiry_time = None
            if ttl is not None:
                expiry_time = time.time() + ttl
            elif self.default_ttl is not None:
                expiry_time = time.time() + self.default_ttl
            if len(self.cache) >= self.capacity:
                self._replace(key)
            node = CacheNode(key, value, expiry_time)
            self.cache[key] = node
            self.t1.append(key)

    def delete(self, key):
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                del self.cache[key]
                if key in self.t1:
                    self.t1.remove(key)
                elif key in self.t2:
                    self.t2.remove(key)
                elif key in self.b1:
                    self.b1.remove(key)
                elif key in self.b2:
                    self.b2.remove(key)

    def hit_rate(self):
        with self.lock:
            if self.hits + self.misses == 0:
                return 0
            return self.hits / (self.hits + self.misses)

def main():
    a = ARC(3)
    a.put(1, 1)
    a.put(2, 2)
    a.put(3, 3)
    a.put(4, 4)
    print(a.get(1))
    print(a.get(2))
    print(a.get(3))


if __name__ == '__main__':
    main()
