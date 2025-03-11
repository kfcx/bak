# -*- coding: utf-8 -*-
# @Time    : 2022/11/15
# @Author  : Naihe
# @File    : 分片.py
# @Software: PyCharm

B = 1024
M = B * B
G = M * B


def calc_divisional_range(filesize):
    fib = Fibonacci(50, filesize)
    arr = [0]
    _temp = 0
    while _temp < filesize:
        x = fib.__next__()
        arr.append(x)
        _temp += x
    arr.append(filesize)
    result = []
    for i in range(len(arr) - 1):
        s_pos, e_pos = arr[i], arr[i + 1] - 1
        result.append([s_pos, e_pos, 1])
    result[-1][-1] = 2
    return result


class Fibonacci(object):
    """斐波那契数列变体迭代器"""

    def __init__(self, n, size):
        """
        :param n:int 指 生成数列的个数
        """
        self.n = n
        self.size = size
        self.rate = M * 20

        # 保存当前生成到的数据列的第几个数据，生成器中性质，记录位置，下一个位置的数据
        self.current = 0
        # 两个初始值
        if size <= M * 20:
            self.a = 0
            self.b = size
        else:
            self.a = 0
            self.b = round(9.103680217851053e-09 * size + 8.708330808866858 * M)

    def __next__(self):
        """当使用next()函数调用时，就会获取下一个数"""
        if self.current < self.n:
            # self.a, self.b = self.b, self.a + self.b
            self.a, self.b = self.b, self.rate + self.b
            self.rate += M * 2
            self.current += 1
            return self.a
        else:
            raise StopIteration

    def __iter__(self):
        """迭代器的__iter__ 返回自身即可"""
        return self


def main():
    size = G * 8
    print(size)
    fib = Fibonacci(100, size)
    arr = [0]
    _temp = 0
    while _temp < size:
        x = fib.__next__()
        arr.append(x)
        _temp = x
    # arr.append(size)
    print(arr)
    print(len(arr))
    exit()

    # generate_range(1024*1024*1024, 11)
    a = calc_divisional_range(size)
    print(a)
    print(len(a))

    exit()

    n = 100
    a = 1024 * 1024 * 10
    d = 1000
    v = ((n + 1) * (2 * a + n * d)) / 2
    print(v)

    exit()
    x = []
    for i in range(1, 10):
        x.append(size * (i * 0.1))
    print(sum(x))
    exit()
    a = calc_divisional_range(size, chunk)
    print(a)


if __name__ == '__main__':
    main()
