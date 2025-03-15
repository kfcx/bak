# -*- coding: utf-8 -*-
# @Time    : 2023/5/20
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : detail.py
# @Software: PyCharm
import ctypes


def jenkins_one_at_a_time_hash(data):
    data_bytes = (ctypes.c_char * len(data)).from_buffer_copy(data)
    hash_value = ctypes.c_uint32(0)

    for i in range(len(data)):
        hash_value.value += ctypes.c_uint8(data_bytes[i]).value
        hash_value.value += (hash_value.value << 10)
        hash_value.value ^= (hash_value.value >> 6)

    hash_value.value += (hash_value.value << 3)
    hash_value.value ^= (hash_value.value >> 11)
    hash_value.value += (hash_value.value << 15)

    return hash_value.value


def popcount(x):
    return bin(x).count("1")


def nearest_power_of_two(x):
    x = ctypes.c_uint32(x - 1)
    x.value |= x.value >> 1
    x.value |= x.value >> 2
    x.value |= x.value >> 4
    x.value |= x.value >> 8
    x.value |= x.value >> 16
    x.value += 1
    return x.value
