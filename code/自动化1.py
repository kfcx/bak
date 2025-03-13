import time

import numpy as np
import socket
from time import sleep
from enum import Enum

DEBUG = True
dprint = print if DEBUG else lambda *args, **kwargs: None


class Touch(Enum):
    UP = 0
    DOWN = 1
    MOVE = 2
    INIT = 9


class Phone(socket.socket):
    def __init__(self, ip: str, dim: tuple):
        super(Phone, self).__init__()
        self.connect((ip, 6000))
        dprint("CONNECTED |", ip)
        self._touch(Touch.INIT, 0, dim)  # Initialize Screen Size

    def __del__(self):
        self.close()

    def send(self, string, **kwargs):
        super(Phone, self).send(string.encode(), **kwargs)
        sleep(0.05)

    def _touch(self, type_: Enum, ind: int, coord: tuple):
        assert 0 < ind <= 20 if type_ is not Touch.INIT else True
        self.send(self._format_touch(type_, ind, coord[0], coord[1]))
        dprint("TOUCH |", type_.name, coord, ind)

    @staticmethod
    def _format_touch(type_, index, x, y):
        return "101{}{:02d}{:05d}{:05d}" \
            .format(type_.value, index, int(x * 10), int(y * 10))

    def touch_down(self, coord: tuple, ind: int = 1):  # 按下
        self._touch(Touch.DOWN, ind, coord)

    def touch_up(self, coord: tuple, ind: int = 1):  # 抬起
        self._touch(Touch.UP, ind, coord)

    def touch_move(self, coord: tuple, ind: int = 1):  # 移动
        self._touch(Touch.MOVE, ind, coord)

    def tap(self, coord: tuple, ind: int = 1):  # 单击
        self.touch_down(coord, ind)
        self.touch_up(coord, ind)

    def swipe(self, coord1: tuple, coord2: tuple, ind: int = 1, smooth=100):  # 滑动屏幕
        self.touch_down(coord1, ind)
        dprint("SWIPE BEGAN |", coord1, ind)

        xs = np.linspace(coord1[0], coord2[0], smooth)
        ys = np.linspace(coord1[1], coord2[1], smooth)
        for x, y in zip(xs, ys):
            self.touch_move((x, y), ind)

        dprint("SWIPE ENDED |", coord2, ind)
        self.touch_up(coord2, ind)

    def open(self, bundle_id):
        self.send(f"11{bundle_id}")
        dprint("OPEN |", bundle_id)

    def alert(self, title, msg):
        self.send(f"12{title};;{msg}")
        dprint("ALERT |", title, ";;", msg)

    def exec(self, cmd):
        self.send(f"13{cmd}")
        dprint("EXEC |", cmd)


if __name__ == '__main__':
    dd = Phone("192.168.1.68", (1242, 2208))

    dd.close()
