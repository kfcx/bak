# -*- coding: utf-8 -*-
# @Time    : 2022/11/13
# @Author  : Naihe
# @File    : minor.py
# @Software: PyCharm
import asyncio
import hashlib
import time

import aiofiles
import aiohttp
import xml.etree.ElementTree as ET

from pathlib import Path
from loguru import logger

from utile import read_file

USER = 1
parentCatalogID = ""


async def uploads(AccessToken, Root, fname, hmd5, length):
    isNeedUpload, url, taskid = await IUploadAndDownload(AccessToken, fname, hmd5, length)
    print(isNeedUpload, url, taskid)
    if isNeedUpload:
        logger.info(taskid)
        await uploadFileServlet(AccessToken, url, length, taskid, Root, fname)
        print(fname, "上传成功")
    else:
        print("秒传完成")


async def IUploadAndDownload(AccessToken, fname, hmd5, length):
    """上传文件引导"""
    url = "http://ose.caiyun.feixin.10086.cn/richlifeApp/devapp/IUploadAndDownload"
    headers = {
        'Host': 'ose.caiyun.feixin.10086.cn:443',
        'Accept': 'text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2',
        'Authorization': 'Basic ' + AccessToken,
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
        <ownerMSISDN>{USER}</ownerMSISDN>
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
        <parentCatalogID>{parentCatalogID}</parentCatalogID>
    </pcUploadFileRequest>"""
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=data, ssl=False) as res:
            _data = await res.text()
    if "not authorized" in _data:
        raise Exception("token失效")
    data = ET.fromstring(_data).find("uploadResult")
    isNeedUpload = int(data.find('newContentIDList').find("newContent").find("isNeedUpload").text)
    if isNeedUpload:
        uploadTaskID = data.find("uploadTaskID").text
        redirectionUrl = data.find("redirectionUrl").text
        return 1, redirectionUrl, uploadTaskID
    else:
        return 0, 0, 0


async def uploadFileServlet(AccessToken, url, length, uploadtaskID, path, pathname):
    """上传文件"""
    headers = {
        'Host': 'upload5.mcloud.139.com',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': str(length),
        'Accept': '*/*',
        'Accept-Encoding': '*',
        'Authorization': 'Basic ' + AccessToken,
        'Content-Type': 'application/octet-stream',
        'Range': f'bytes=0-{length}',
        'contentSize': str(length),
        'uploadtaskID': uploadtaskID,
        "x-DeviceInfo": "",
        "x-MM-Source": "001",
        "x-deviceID": "",
        'x-huawei-channelSrc': '10200153',
    }
    async with aiofiles.open(path / pathname, "rb") as f:
        logger.info(f"uploadFileServlet: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=f) as res:
                logger.info(f"uploadFileServlet: {res.status}")
                print(await res.text())


def calc_divisional_range(filesize, chuck=10):
    step = filesize//chuck
    arr = list(range(0, filesize, step))
    result = []
    for i in range(len(arr)-1):
        s_pos, e_pos = arr[i], arr[i+1]-1
        result.append([s_pos, e_pos])
    result[-1][-1] = filesize-1
    return result



async def main():
    AccessToken = ""
    Root = Path(r"Downloads")
    filename = "lineage-.zip"
    hmd5, length = await read_file(Root / filename)
    slice_size = 100 * 1024 * 10
    index = 0
    divisional_ranges = calc_divisional_range(length, 20)
    isNeedUpload, url, taskid = await IUploadAndDownload(AccessToken, filename, hmd5, length)
    print(isNeedUpload, url, taskid)

    loop = asyncio.get_event_loop()

    tasks = [uploadFileServlet(AccessToken, url, length, taskid, Root, filename)
             for s_pos, e_pos in divisional_ranges]
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
