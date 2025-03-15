# -*- coding: utf-8 -*-
# @Time    : 2023/5/20
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : bloom_filter.py
# @Software: PyCharm
import math
import mmh3
from bitarray import bitarray


class BloomFilter:
    def __init__(self, capacity, false_positive_error_rate=0.01):
        self.capacity = capacity
        self.false_positive_error_rate = false_positive_error_rate
        self.bitset_size = self.best_bitset_size(capacity, false_positive_error_rate)
        self.num_hashes = self.best_num_hashes(capacity, false_positive_error_rate)
        self.bitset = bitarray(self.bitset_size)
        self.bitset.setall(False)

    def contains(self, item):
        for i in range(self.num_hashes):
            index = self.double_hash(item, i)
            if not self.bitset[index]:
                return False
        return True

    def record_access(self, item):
        for i in range(self.num_hashes):
            index = self.double_hash(item, i)
            self.bitset[index] = True

    def clear(self):
        self.bitset.setall(False)

    @staticmethod
    def best_bitset_size(capacity, error_rate):
        return math.ceil(-1 * capacity * math.log(error_rate) / math.pow(math.log(2), 2))

    @staticmethod
    def best_num_hashes(capacity, error_rate):
        bitset_size = BloomFilter.best_bitset_size(capacity, error_rate)
        return round(math.log(2) * bitset_size / float(capacity))

    def double_hash(self, item, i):
        hash1 = mmh3.hash64(item, seed=0)[0]
        hash2 = mmh3.hash64(item, seed=1)[0]
        return (hash1 + i * hash2) % self.bitset_size
