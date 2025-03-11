# -*- coding: utf-8 -*-
# @Time    : 2023/3/3
# @Author  : Naihe
# @File    : hash.py
# @Software: PyCharm
import time


class Snowflake:
    def __init__(self, datacenter_id, machine_id):
        self.datacenter_id = datacenter_id
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1

    def generate_id(self):
        timestamp = int(time.time() * 1000)
        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id.")
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095
            if self.sequence == 0:
                timestamp = self.wait_next_millis(timestamp)
        else:
            self.sequence = 0
        self.last_timestamp = timestamp
        return ((timestamp - 1288834974657) << 22) | (self.datacenter_id << 12) | (self.machine_id << 2) | self.sequence

    def wait_next_millis(self, current_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= current_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp


snowflake = Snowflake(datacenter_id=1, machine_id=1)
