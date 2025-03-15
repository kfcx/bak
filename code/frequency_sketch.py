# -*- coding: utf-8 -*-
# @Time    : 2023/5/20
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : frequency_sketch.py
# @Software: PyCharm
import numpy as np
import mmh3
import math


class FrequencySketch:
    def __init__(self, capacity):
        self.change_capacity(capacity)
        self.size_ = 0

    def change_capacity(self, n):
        if n <= 0:
            raise ValueError("FrequencySketch capacity must be larger than 0")
        self.table_ = np.zeros(self.nearest_power_of_two(n), dtype=np.uint64)

    def contains(self, t):
        return self.frequency(t) > 0

    def frequency(self, t):
        hash = self.hash(t)
        frequency = np.iinfo(np.int32).max

        for i in range(4):
            frequency = min(frequency, self.get_count(hash, i))

        return frequency

    def record_access(self, t):
        hash = self.hash(t)
        was_added = False

        for i in range(4):
            was_added |= self.try_increment_counter_at(hash, i)

        if was_added:
            self.size_ += 1
            if self.size_ == self.sampling_size():
                self.reset()

    def get_count(self, hash, counter_index):
        table_index = self.table_index(hash, counter_index)
        offset = self.counter_offset(hash, counter_index)
        return (self.table_[table_index] >> offset) & 0xf

    def table_index(self, hash, counter_index):
        seeds = [0xc3a5c85c97cb3127, 0xb492b66fbe98f273, 0x9ae16a3b2f90404f, 0xcbf29ce484222325]
        h = seeds[counter_index] * hash
        h += h >> 32
        return h & (len(self.table_) - 1)

    def try_increment_counter_at(self, hash, counter_index):
        index = self.table_index(hash, counter_index)
        offset = self.counter_offset(hash, counter_index)
        if self.can_increment_counter_at(index, offset):
            self.table_[index] += 1 << offset
            return True
        return False

    def counter_offset(self, hash, counter_index):
        return self.offset_multiplier(hash) + counter_index << 2

    def offset_multiplier(self, hash):
        return (hash & 3) << 2

    def can_increment_counter_at(self, table_index, offset):
        mask = 0xf << offset
        return (self.table_[table_index] & mask) != mask

    def reset(self):
        self.table_ = (self.table_ >> 1) & 0x7777777777777777
        self.size_ //= 2

    def sampling_size(self):
        return len(self.table_) * 10

    @staticmethod
    def hash(value):
        return mmh3.hash64(str(value), seed=0, signed=False)[0]

    @staticmethod
    def nearest_power_of_two(n):
        return 1 << (n - 1).bit_length()
