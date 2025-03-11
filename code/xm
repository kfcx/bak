#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import asyncio
import time
from datetime import datetime

import aiohttp
import requests
from aiohttp import ClientSession
from loguru import logger

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
}
DEBUG = False


class Timer(object):
    def __init__(self, sleep_interval=0.5):
        # buy_time = '2020-12-22 09:59:59.500'
        # 修改成几点几分几秒几毫秒
        self.buy_time = "9:59:58.300000"
        # 每天的最后购买时间
        self.last_purchase_time = "10:00:03.000"
        # 误差时间调整
        self.step_error_time_ms = 993

        localtime = time.localtime(time.time())
        buy_time_everyday = self.buy_time.__str__()
        last_purchase_time_everyday = self.last_purchase_time.__str__()

        # 最后购买时间
        last_purchase_time = datetime.strptime(
            localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__() + ' ' + last_purchase_time_everyday,
            "%Y-%m-%d %H:%M:%S.%f")

        buy_time_config = datetime.strptime(
            localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__() + ' ' + buy_time_everyday,
            "%Y-%m-%d %H:%M:%S.%f")

        if time.mktime(localtime) < time.mktime(buy_time_config.timetuple()):
            # 取正确的购买时间
            self.buy_time = buy_time_config
        # elif time.mktime(localtime) > time.mktime(last_purchase_time.timetuple()):
        #     # 取明天的时间 购买时间
        #     self.buy_time = datetime.strptime(
        #         localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + (
        #                 localtime.tm_mday + 1).__str__() + ' ' + buy_time_everyday,
        #         "%Y-%m-%d %H:%M:%S.%f")
        else:
            self.buy_time = datetime.strptime(
                localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + (
                        localtime.tm_mday + 1).__str__() + ' ' + buy_time_everyday,
                "%Y-%m-%d %H:%M:%S.%f")

        # self.buy_time = buy_time_config
        print("购买时间：{}".format(self.buy_time))

        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.sleep_interval = sleep_interval

        # self.diff_time = self.local_jd_time_diff()
        self.diff_time = 0

    def jd_time(self):
        """
        从京东服务器获取时间毫秒
        :return:
        """
        try:
            url = "https://time.hd.mi.com/gettimestamp"
            res = requests.get(url=url, verify=False).text
            return int(res.split("=")[1])
        except Exception:
            return 0

    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        step_error_time_ms = self.step_error_time_ms
        return int(round(time.time() * 1000)) - int(step_error_time_ms)

    def local_jd_time_diff(self):
        """
        计算本地与京东服务器时间差
        :return:
        """
        return self.local_time() - self.jd_time()

    def start(self):
        logger.info('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(self.buy_time, self.diff_time))
        while True:
            # 本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
            # 具体精度依赖获取京东服务器时间的网络时间损耗
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)


async def hello(url, semaphore, activity_code):
    data = {
        "activity_code": activity_code
    }
    Timeout = aiohttp.ClientTimeout(total=1)
    try:
        async with semaphore:
            async with ClientSession(headers=headers, timeout=Timeout) as session:
                async with session.post(url, data=data, ssl=False) as response:
                    if DEBUG:
                        logger.info(await response.json())
    except Exception:
        pass


async def acode(_):
    data = {
        "page_id": "287",
    }
    url = "https://m.mi.com/v1/home/page_struct"
    Timeout = aiohttp.ClientTimeout(total=1)
    try:
        async with ClientSession(headers=headers, timeout=Timeout) as session:
            async with session.post(url, data=data, ssl=False) as response:
                res = await response.json()
                for i in res['data']['floors']:
                    # if "分时段抢券" in i['data']['components_name']:
                    if i['data']['title0'] == "抢红包":
                        for j in i['data']['body']['items']:
                            _.append(j['activity_code'])
                        # print(i['data']['body']['items'][1]['activity_code'], i['data']['body']['items'][1]['activity_id'])
    except Exception:
        return [""]


def run(data):
    url = "https://m.mi.com/v1/activity/page_draw"
    semaphore = asyncio.Semaphore(100)
    to_get = [hello(url, semaphore, _) for _ in data]
    return to_get


def draw(activity_code):
    url = "https://m.mi.com/v1/activity/page_draw"
    data = {
        "activity_code": activity_code
    }
    res = requests.post(url=url, headers=headers, data=data)
    print(res.json())


def query():
    data = {
    }
    url = "https://m.mi.com/v1/activity/page_draw_query"
    res = requests.post(url=url, headers=headers, data=data)
    print(res.json()['data']['activity_list'])
    #  {'status': 1, 'text': '抢到啦'},
    #  {'status': 3, 'text': '已抢光'},
    #  { status: 2, text: "正在疯抢" }


if __name__ == '__main__':
    data = []
    Timer().start()
    for i in range(15):
        # if len(data):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(run(data)))
