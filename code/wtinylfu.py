# -*- coding: utf-8 -*-
# @Time    : 2023/5/20
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : wtinylfu.py
# @Software: PyCharm
from collections import deque, OrderedDict
from typing import Dict, Deque, Any, Tuple, Union
from math import ceil
from typing import Callable, Optional, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class FrequencySketch:
    def __init__(self, capacity: int):
        self.capacity = capacity

    def record_access(self, key: K):
        pass  # 记录访问

    def change_capacity(self, n: int):
        self.capacity = n

    def frequency(self, key: K) -> int:
        return 1  # 返回key的频率


class CachePage:
    def __init__(self, key: K, data: Optional[V] = None):
        self.key = key
        self.data = data


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: deque[CachePage] = deque()

    def size(self) -> int:
        return len(self.cache)

    def is_full(self) -> bool:
        return self.size() == self.capacity

    def insert(self, key: K, data: V) -> CachePage:
        new_page = CachePage(key, data)
        self.cache.append(new_page)
        if self.is_full():
            self.cache.popleft()
        return new_page

    def lru_pos(self) -> CachePage:
        return self.cache[0]

    def evict(self):
        self.cache.popleft()

    def victim_key(self) -> K:
        return self.lru_pos().key

    def handle_hit(self, page: CachePage):
        self.cache.remove(page)
        self.cache.append(page)

    def set_capacity(self, n: int):
        self.capacity = n

    def transfer_page_from(self, page: CachePage, other_cache: "LRUCache"):
        other_cache.cache.remove(page)
        self.cache.append(page)

    def erase(self, page: CachePage):
        self.cache.remove(page)


class WTinyLFUCache:
    def __init__(self, capacity: int):
        self.filter = FrequencySketch(capacity)
        self.window = LRUCache(self.window_capacity(capacity))
        self.main = LRUCache(capacity - self.window.capacity)
        self.page_map: Dict[K, CachePage] = {}

    def size(self) -> int:
        return self.window.size() + self.main.size()

    def capacity(self) -> int:
        return self.window.capacity + self.main.capacity

    @staticmethod
    def window_capacity(total_capacity: int) -> int:
        return max(1, int(ceil(0.01 * total_capacity)))

    def change_capacity(self, n: int):
        self.filter.change_capacity(n)
        self.window.set_capacity(self.window_capacity(n))
        self.main.set_capacity(n - self.window.capacity)

    def get(self, key: K) -> Optional[V]:
        self.filter.record_access(key)
        page = self.page_map.get(key)
        if page is not None:
            if page in self.window.cache:
                self.window.handle_hit(page)
            else:
                self.main.handle_hit(page)
            return page.data
        return None

    def insert(self, key: K, value: V):
        if self.window.is_full():
            self.evict()
        if key in self.page_map:
            self.page_map[key].data = value
        else:
            new_page = self.window.insert(key, value)
            self.page_map[key] = new_page

    def evict(self):
        if self.size() >= self.capacity():
            self.evict_from_window_or_main()
        else:
            self.main.transfer_page_from(self.window.lru_pos(), self.window)

    def evict_from_window_or_main(self):
        window_victim_freq = self.filter.frequency(self.window.victim_key())
        main_victim_freq = self.filter.frequency(self.main.victim_key())
        if window_victim_freq > main_victim_freq:
            self.evict_from_main()
            self.main.transfer_page_from(self.window.lru_pos(), self.window)
        else:
            self.evict_from_window()

    def evict_from_main(self):
        del self.page_map[self.main.victim_key()]
        self.main.evict()

    def evict_from_window(self):
        del self.page_map[self.window.victim_key()]
        self.window.evict()

    def erase(self, key: K):
        if key in self.page_map:
            page = self.page_map[key]
            if page in self.window.cache:
                self.window.erase(page)
            else:
                self.main.erase(page)
            del self.page_map[key]

    def get_and_insert_if_missing(self, key: K, value_loader: Callable[[K], V]) -> V:
        value = self.get(key)
        if value is None:
            value = value_loader(key)
            self.insert(key, value)
        return value


# 使用示例
def value_loader(key: str) -> str:
    return f"Value for {key}"


if __name__ == '__main__':
    cache = WTinyLFUCache(100)

    # 插入值
    cache.insert("key1", "value1")

    # 获取值
    value = cache.get("key1")
    print(value)  # 输出 "value1"

    # 获取并插入缺失值
    value = cache.get_and_insert_if_missing("key2", value_loader)
    print(value)  # 输出 "Value for key2"
