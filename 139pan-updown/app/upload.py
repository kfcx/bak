# -*- coding: utf-8 -*-
# @Time    : 2022/11/10
# @Author  : Naihe
# @File    : upload.py
# @Software: PyCharm
import asyncio
import hashlib
import random
import sys
import time
from pathlib import Path
import aiofiles.os

import aiofiles
import aiohttp
import requests
import xml.etree.ElementTree as ET
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import BoundedSemaphore

try:
    from app.config import AccessToken, M, USER, parentCatalogID, CHUNK_SIZE, STATIC_ROOT
except ModuleNotFoundError:
    from config import AccessToken, M, USER, parentCatalogID, STATIC_ROOT, CHUNK_SIZE


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
            self.a = 0  # 0
            self.b = size  # 1
        else:
            # self.b = round(9.103680217851053e-09 * size + 8.708330808866858 * M)
            self.b = M * 10
            self.a = 0

    def __next__(self):
        """当使用next()函数调用时，就会获取下一个数"""
        if self.current < self.n:
            # self.a, self.b = self.b, self.a + self.b  # 原始
            self.a, self.b = self.b, self.rate + self.b
            self.rate += M * 25
            self.current += 1
            return self.a
        else:
            raise StopIteration

    def __iter__(self):
        """迭代器的__iter__ 返回自身即可"""
        return self


def calc_avg_range(filesize, chuck=10):
    chuck = 2 if chuck < 2 else chuck
    step = filesize // chuck
    arr = list(range(0, filesize, step))
    result = []
    for i in range(len(arr) - 1):
        s_pos, e_pos = arr[i], arr[i + 1] - 1
        result.append([s_pos, e_pos, 1, 0])
    result[-1][-2] = 2
    result[-1][-3] = filesize
    return result


def calc_up_range(filesize):
    fib = Fibonacci(100, filesize)
    arr = [0]
    _temp = 0
    while _temp < filesize:
        x = fib.__next__()
        arr.append(x)
        _temp = x
    result = []
    for i in range(len(arr) - 1):
        s_pos, e_pos = arr[i], arr[i + 1] - 1
        result.append([s_pos, e_pos, 1, i + i])
    result[-1][-2] = 2
    result[-1][-3] = filesize
    return result


class distran:
    def __init__(self, AccessToken, USER, parentCatalogID):
        self.AccessToken = AccessToken
        self.USER = USER
        self.parentCatalogID = parentCatalogID
        # self.sem = asyncio.Semaphore(5)
        self.sem = BoundedSemaphore(value=5)

    def getDisk(self):
        """获取文件列表相信"""
        url = "https://ose.caiyun.feixin.10086.cn/richlifeApp/devapp/ICatalog"
        self.AccessToken = ""
        headers = {
            'Host': 'ose.caiyun.feixin.10086.cn',
            'Accept': 'text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2',
            "Authorization": "Basic " + self.AccessToken,
            'Connection': 'Keep-Alive',
            'Content-Type': 'text/xml;UTF-8',
            'clientId': 'pcapp',
            'msgId': '',  #
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en,*',
            'User-Agent': 'Mozilla/5.0',
        }
        data = f"""<?xml version='1.0' encoding='utf-8'?>
          <getDisk>
          <MSISDN>{self.USER}</MSISDN>
          <catalogID>1</catalogID>
          <filterType>0</filterType>
          <catalogSortType>0</catalogSortType>
          <contentType>0</contentType>
          <contentSortType>0</contentSortType>
          <sortDirection>0</sortDirection>
          <startNumber>1</startNumber>
          <endNumber>100</endNumber>
          <catalogType>-1</catalogType>
          <auditFilterFlag>2</auditFilterFlag>
          </getDisk>"""
        res = requests.post(url, headers=headers, data=data)
        print(res.status_code)
        print(res.text)
        return res.text

    def downloadRequest(self, contentID):
        """获取下载直链"""
        url = "https://ose.caiyun.feixin.10086.cn/richlifeApp/devapp/IUploadAndDownload"
        headers = {
            'Host': 'ose.caiyun.feixin.10086.cn:443',
            'Accept': 'text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2',
            'Authorization': 'Basic ' + self.AccessToken,
            'Connection': 'keep-alive',
            'Content-Type': 'text/xml;UTF-8',
            'x-huawei-channelSrc': '10200153',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en,*',
            'User-Agent': 'Mozilla/5.0',
        }
        data = f'<?xml version="1.0" encoding="utf-8"?><downloadRequest><appName /><MSISDN>{self.USER}</MSISDN><contentID>{contentID}</contentID><OwnerMSISDN /><entryShareCatalogID /><operation>0</operation><fileVersion>-1</fileVersion></downloadRequest>'
        with requests.post(url, headers=headers, data=data) as res:
            print(ET.fromstring(res.text).find("String").text)

    async def pcUploadFileRequest(self, fname, hmd5, length):
        """上传文件引导"""
        url = "http://ose.caiyun.feixin.10086.cn/richlifeApp/devapp/IUploadAndDownload"
        headers = {
            'Host': 'ose.caiyun.feixin.10086.cn:443',
            'Accept': 'text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2',
            'Authorization': 'Basic ' + self.AccessToken,
            'Connection': 'keep-alive',
            'Content-Type': 'text/xml;UTF-8',
            "x-DeviceInfo": "",
            "x-MM-Source": "001",
            "x-deviceID": "",
            'x-huawei-channelSrc': '10200153',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en,*',
            'User-Agent': 'Mozilla/5.0',
        }
        data = f"""<?xml version="1.0" encoding="utf-8"?>
        <pcUploadFileRequest>
            <ownerMSISDN>{self.USER}</ownerMSISDN>
            <fileCount>1</fileCount>
            <totalSize>{length}</totalSize>
            <uploadContentList length="1">
                <uploadContentInfo>
                    <contentName>{fname}</contentName>
                    <contentSize>{length}</contentSize>
                    <contentDesc></contentDesc>
                    <contentTAGList></contentTAGList>
                    <comlexFlag>0</comlexFlag>
                    <comlexCID></comlexCID>
                    <resCID length="0"></resCID>
                    <digest>{hmd5}</digest>
                </uploadContentInfo>
            </uploadContentList>
            <newCatalogName></newCatalogName>
            <parentCatalogID>{self.parentCatalogID}</parentCatalogID>
        </pcUploadFileRequest>"""
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=data) as res:
                _data = await res.text()
                print(_data)
        if "not authorized" in _data:
            raise Exception("token失效")
        data = ET.fromstring(_data).find("uploadResult")
        isNeedUpload = int(data.find('newContentIDList').find("newContent").find("isNeedUpload").text)
        if isNeedUpload:
            uploadTaskID = data.find("uploadTaskID").text
            redirectionUrl = data.find("redirectionUrl").text
            contentID = data.find("newContentIDList").find("newContent").find("contentID").text
            return 1, redirectionUrl, uploadTaskID, contentID
        else:
            return 0, 0, 0, 0

    async def syncUploadTaskInfo(self, uploadTaskID, contentID):
        url = "http://ose.caiyun.feixin.10086.cn/richlifeApp/devapp/IUploadAndDownload"
        headers = {
            'Host': 'ose.caiyun.feixin.10086.cn:443',
            'Accept': 'text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2',
            'Authorization': 'Basic ' + self.AccessToken,
            'Connection': 'keep-alive',
            'Content-Type': 'text/xml;UTF-8',
            "x-DeviceInfo": "",
            "x-MM-Source": "001",
            "x-deviceID": "",
            'x-huawei-channelSrc': '10200153',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en,*',
            'User-Agent': 'Mozilla/5.0',
        }
        data = f"""<?xml version="1.0" encoding="utf-8"?>
    <syncUploadTaskInfo>
        <account>{self.USER}</account>
        <taskList length = "1">
            <liteTaskInfo>
                <taskID>{uploadTaskID}</taskID>
                <contentID>{contentID}</contentID>
            </liteTaskInfo>
        </taskList>
    </syncUploadTaskInfo>"""
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=data) as res:
                _data = await res.text()
        assert "not authorized" not in _data
        data = ET.fromstring(_data)
        _temp = [i for i in data.itertext()]
        # print(_data)
        assert "<resultCode>0" in _data

    async def uploadFileServlet_async(self, url, curlen, endlen, length, uploadtaskID, path, rangeType,
                                      sleep):
        """上传文件"""
        # await asyncio.sleep(random.uniform(sleep, sleep + 0.2))  # 随机延时
        headers = {
            'Host': 'upload5.mcloud.139.com',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 'Connection': 'keep-alive',
            'Connection': 'close',
            'Content-Length': str(endlen - curlen),
            'Accept': '*/*',
            "rangeType": f"{rangeType}",
            'Accept-Encoding': '*',
            'Authorization': 'Basic ' + self.AccessToken,
            # 'Content-Type': f'application/octet-stream; name={path.name}',
            'Content-Type': f'application/octet-stream',
            'Range': f'bytes={curlen}-{endlen}',
            'contentSize': str(length),
            'uploadtaskID': uploadtaskID,
            "x-DeviceInfo": "",
            "x-MM-Source": "001",
            "x-deviceID": "",
            'x-huawei-channelSrc': '10200153',
        }
        sem = asyncio.Semaphore(5)
        async with sem:
            async with aiofiles.open(path, "rb") as f:
                await f.seek(curlen)
                logger.info(f"uploading: {endlen}, {rangeType}, {sleep}")
                async with aiohttp.ClientSession() as session:
                    async with session.post(url=url, headers=headers, data=await f.read(endlen - curlen + 1)) as res:
                        logger.info(f"uploadFileServlet: {res.status} {sleep} {await res.text()}")
                        print(res.headers.get("Content-Range"), headers.get("Range"))

    def uploadFileServlet_thread(self, url, curlen, endlen, length, uploadtaskID, path, rangeType, sleep):
        """上传文件"""
        time.sleep(sleep)
        headers = {
            'Host': 'upload5.mcloud.139.com',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': str(endlen - curlen),
            'Accept': '*/*',
            "rangeType": f"{rangeType}",
            'Accept-Encoding': '*',
            'Authorization': 'Basic ' + self.AccessToken,
            'Content-Type': 'application/octet-stream',
            'Range': f'bytes={curlen}-{endlen}',
            'contentSize': str(length),
            'uploadtaskID': uploadtaskID,
            "x-DeviceInfo": "",
            "x-MM-Source": "001",
            "x-deviceID": "",
            'x-huawei-channelSrc': '10200153',
        }
        with self.sem:
            with open(path, "rb") as f:
                f.seek(curlen)
                logger.info(f"uploading: {endlen}, {rangeType}, {sleep}")
                with requests.post(url=url, headers=headers, data=f.read(endlen - curlen + 1), stream=True) as res:
                    logger.info(f"uploadFileServlet: {res.status_code} {sleep} {res.text}")
                    print(res.headers.get("Content-Range"), headers.get("Range"))
                    assert res.status_code == 200


py = distran(AccessToken, USER, parentCatalogID)


async def uploads(fname, hmd5, length):
    # divisional_ranges = calc_up_range(length)
    divisional_ranges = calc_avg_range(length)
    print(divisional_ranges)
    isNeedUpload, url, taskid, contentID = await py.pcUploadFileRequest(fname.name, hmd5, length)
    logger.info(f"开始上传 {fname.name}")
    print(isNeedUpload, taskid, contentID, url)
    if isNeedUpload:
        logger.info(taskid)
        slast, elast, rType, leep = divisional_ranges.pop()
        with ThreadPoolExecutor() as p:  # 多线程
            futures = [p.submit(py.uploadFileServlet_thread, url, s_pos, e_pos, length, taskid, fname, rangeType, sleep)
                       for s_pos, e_pos, rangeType, sleep in divisional_ranges]
            as_completed(futures)
        # Thread(target=py.uploadFileServlet_thread, args=(url, slast, elast, length, taskid, fname, rType, leep)).start()
        py.uploadFileServlet_thread(url, slast, elast, length, taskid, fname, rType, leep)
        # loop = asyncio.get_event_loop()   # 异步
        # tasks = [py.uploadFileServlet_async(url, s_pos, e_pos, length, taskid, contentID, fname, rangeType, sleep)
        #          for s_pos, e_pos, rangeType, sleep in divisional_ranges]
        # loop.run_until_complete(asyncio.wait(tasks))
        print(fname.name, "上传成功")
        # await aiofiles.os.remove(fname)
    else:
        print("秒传完成")


def main(cmd, args):
    if cmd != "upload" or args is None:
        logger.warning("不正确的命令")
        return 0
    loop = asyncio.new_event_loop()
    # Root = Path(r"Downloads")
    # filename = "aria2-1.36.0-win-64bit-build1.zip"
    filename = Path(STATIC_ROOT / args[0])
    # filename = Path(Root/filename)
    md5 = hashlib.md5()
    # with open(filename, "rb") as f:
    #     while chunk := f.read(CHUNK_SIZE):
            # md5.update(chunk)
    # hmd5 = md5.hexdigest()
    length = filename.stat().st_size
    hmd5 = hashlib.md5((str(time.time()) + filename.name).encode()).hexdigest()
    # length = round((Root / filename).stat().st_size)
    print(hmd5, length)
    # exit()
    loop.run_until_complete(uploads(filename, hmd5, length))
    # divisional_ranges = calc_up_range(length)
    # print(len(divisional_ranges), divisional_ranges)
    # exit()
    # isNeedUpload, url, taskid, contentID = loop.run_until_complete(py.pcUploadFileRequest(filename, hmd5, length))
    # print(isNeedUpload, taskid, contentID, url)
    # for s_pos, e_pos, rangeType, sleep in divisional_ranges:
    #     loop.run_until_complete(
    #         py.uploadFileServlet(url, s_pos, e_pos, length, taskid, contentID, Root / filename, rangeType, sleep)
    #     )
    # exit()


if __name__ == '__main__':
    a = py.getDisk()
    print(a)

    logger.info(f"开始执行 {str(sys.argv)}")
    with open(STATIC_ROOT / "log.txt", "w") as f:
        f.write(f"开始执行 {str(sys.argv)}")
    if len(sys.argv) >= 2:
        cmd, args = (sys.argv[1], []) if len(sys.argv) == 2 else (sys.argv[1], [*sys.argv[2:]])
        main(cmd, args)
    else:
        main("upload", sys.argv[1:])
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # asyncio.run(main())

