# -*- coding: utf-8 -*-
# @Time    : 2022/11/14
# @Author  : Naihe
# @File    : 断点续传.py
# @Software: PyCharm
import datetime
import hashlib
import json
import random
import string
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread, BoundedSemaphore

import requests
import xml.etree.ElementTree as ET

from loguru import logger

from config import M

request = requests.session()
getRealId = lambda v: [v.split('/').pop().replace("~", ""), v.count('~') != 0, "/".join(v.split('/')[0: -1])]
getRandomSring = lambda e: ''.join(random.choices(string.ascii_letters + string.digits, k=e))
cookie = ''
mobile = ""
# 下载地址
# download.mcloud.139.com  广州移动
# download.mcloud.10086.cn  呼和浩特移动

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
            # self.b = round(9.103680217851053e-09 * size + 8.708330808866858 * M)
            self.b = M * 10
            self.a = 0

    def __next__(self):
        """当使用next()函数调用时，就会获取下一个数"""
        if self.current < self.n:
            # self.a, self.b = self.b, self.a + self.b
            self.a, self.b = self.b, self.rate + self.b
            self.rate += M * 25
            self.current += 1
            return self.a
        else:
            raise StopIteration

    def __iter__(self):
        """迭代器的__iter__ 返回自身即可"""
        return self


def resumeUpload(uploadId, retry=2):
    taskId, path, contentId = uploadId.split('-')
    params = {
        "account": '',
        "taskList": [{
            "contentID": contentId,
            "path": path,
            "taskID": taskId
        }],
        "commonAccountInfo": {"account": mobile, "accountType": 1}
    }

    with request.post('https://yun.139.com/orchestration/personalCloud/uploadAndDownload/v1.0/syncUploadTaskInfo',
                      data=params, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                "Cookie": cookie,
                **createHeaders(params),
            }) as res:
        data = res.json()
    if data['code'] == '1010010014' or retry > 0:
        return resumeUpload(uploadId, retry - 1)
    if not data['success']:
        return {
            'error': {'message': '[' + data['data']['result']['resultCode'] + ']' + data['message']}
        }

    return {
        "start": [data['data']['array'][0]['fileUploadInfos'][0]['pgs'], taskId, contentId],
        "uploadUrl": data['data']['array'][0]['uploadURL']
    }


def beforeUpload(parent_id, name, size, md5):
    fid = getRealId(parent_id)
    params = {
        "manualRename": 2,
        "operation": 0,
        "fileCount": 1,
        "totalSize": size,
        "uploadContentList": [{
            "contentName": name,
            "contentSize": size,
            # "digest": md5
        }],
        "parentCatalogID": fid,
        "newCatalogName": "",
        "commonAccountInfo": {"account": mobile, "accountType": 1}
    }
    if md5:
        params['uploadContentList'][0]['digest'] = md5
    print(params)
    headers = createHeaders(params)
    with request.post('https://yun.139.com/orchestration/personalCloud/uploadAndDownload/v1.0/pcUploadFileRequest',
                      data=params, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                "Cookie": cookie,
                **headers,
            }) as res:
        data = res.json()
    if not data['success']:
        return {
            'error': {'message': data['message']}
        }
    if data['data']['result']['resultCode'] != '0':
        return {
            'error': {'message': data['data']['result']['resultDesc']}
        }
    res = data['data']['uploadResult']
    return {
        "uploadUrl": res['redirectionUrl'],
        "taskId": res['uploadTaskID'],
        "contentId": res['newContentIDList'][0]['contentID']
    }


def upload2(parent_id, stream, size, name, manual, **rest):
    fid = getRealId(parent_id)
    print('UPLOAD', rest['uploadId'])
    if rest['uploadId']:
        res = resumeUpload(rest['uploadId'])
    else:
        res = beforeUpload(parent_id, name, size, **rest)

    # 恢复状态发生错误，尝试重新创建
    if rest['uploadId'] and res['error']:
        print(('create new upload session', res['error']))
        res = beforeUpload(parent_id, name, size, **rest)
    uploadUrl, taskId, contentId, start = res['uploadUrl'], res['taskId'], res['contentId'], 0

    # fast upload
    if not uploadUrl:
        print('fast upload success')
        # no need
        ret = {'id': parent_id + '/~' + contentId, 'name': name, 'parent_id': parent_id}
        if manual:
            ret['completed'] = True
        return ret
    uploadId = f'{taskId}-{fid}-{contentId}'

    def done(stream):
        with request.post(uploadUrl, data=stream, headers={
            'Accept': '*/*',
            'Content-Type': f'text/plain;name={name}',
            'contentSize': size,
            'range': f'bytes={start}-{size - 1}',
            'content-length': size - start,
            'uploadtaskID': taskId,
            'rangeType': 0,
            'Referer': 'https://yun.139.com/',
            'x-SvcType': 1,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }) as res:
            data = res.text
            if res.status_code != 200:
                return {
                    'error': {'message': data}
                }
        return {
            'id': parent_id + '/~' + contentId,
            'name': name,
            'parent_id': parent_id,
            'uploadId': uploadId,
        }

    if manual:
        return {
            'uploadId': uploadId,
            'start': start,
            'done': done
        }
    else:
        return done(stream)


def createHeaders(body):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    key = getRandomSring(16)
    sign = hashlib.md5(hashlib.md5(json.dumps(body).replace(' ', '').encode()).hexdigest().encode()).hexdigest().upper()
    headers = {
        'x-huawei-channelSrc': '10000034',
        'x-inner-ntwk': '2',
        'mcloud-channel': '1000101',
        'mcloud-client': '10701',
        'mcloud-sign': f"{timestamp},{key},{sign}",
        'content-type': "application/json;charset=UTF-8",
        'caller': 'web',
        'CMS-DEVICE': 'default',
        'x-DeviceInfo': '',
        'x-SvcType': '1',
        'referer': 'https://yun.139.com/w/',
    }
    return headers


class distran:
    def __init__(self, AccessToken=None):
        AccessToken = ""
        self.AccessToken = AccessToken
        self.USER = 1
        self.parentCatalogID = ""
        self.sem = BoundedSemaphore(value=5)

    def pcUploadFileRequest(self, fname, hmd5, length):
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
        with requests.post(url=url, headers=headers, data=data.encode("utf-8")) as res:
            _data = res.text
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

    def syncUploadTaskInfo(self, uploadTaskID, contentID):
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
<syncUploadTaskInfo>
    <account>{self.USER}</account>
    <taskList length = "1">
        <liteTaskInfo>
            <taskID>{uploadTaskID}</taskID>
            <contentID>{contentID}</contentID>
        </liteTaskInfo>
    </taskList>
</syncUploadTaskInfo>"""
        with requests.post(url=url, headers=headers, data=data) as res:
            _data = res.text
        assert "not authorized" not in _data
        data = ET.fromstring(_data)
        _temp = [i for i in data.itertext()]
        print(_data)
        # assert "<resultCode>0" in _data

    def uploadFileServlet(self, url, curlen, endlen, length, uploadtaskID, path, rangeType, sleep):
        """上传文件"""
        # time.sleep(sleep)
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
                    # assert res.status_code == 200

    def calc_divisional_range2(self, filesize, chuck=10):
        chuck = 2 if chuck < 2 else chuck
        step = filesize // chuck
        arr = list(range(0, filesize, step))
        result = []
        for i in range(len(arr) - 1):
            s_pos, e_pos = arr[i], arr[i + 1] - 1
            result.append([s_pos, e_pos, 1, i])
        result[-1][-2] = 2
        result[-1][-3] = filesize
        return result

    def calc_divisional_range(self, filesize):
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


def main():
    py = distran()
    Root = Path(r"Downloads")
    filename = "愛 して、アミーゴ - 浪川大輔.mp4"

    length = round((Root / filename).stat().st_size)
    hmd5 = hashlib.md5((str(time.time()) + filename).encode()).hexdigest()
    print(hmd5, length)

    isNeedUpload, redirectionUrl, uploadTaskID, contentID = py.pcUploadFileRequest(filename, hmd5, length)
    if isNeedUpload:
        divisional_ranges = py.calc_divisional_range(length)
        print(divisional_ranges, end="\n" * 2)
        slast, elast, rType, leep = divisional_ranges.pop()
        with ThreadPoolExecutor() as p:
            futures = [
                p.submit(py.uploadFileServlet, redirectionUrl, s_pos, e_pos, length, uploadTaskID, Root / filename,
                         rangeType, sleep)
                for s_pos, e_pos, rangeType, sleep in divisional_ranges]
            as_completed(futures)
        py.uploadFileServlet(redirectionUrl, slast, elast, length, uploadTaskID, Root / filename,
        rType, leep)

        ## 单线程
        # for s_pos, e_pos, rangeType, sleep in divisional_ranges:
        #     py.uploadFileServlet(redirectionUrl, s_pos, e_pos, length, uploadTaskID, Root / filename, rangeType, sleep)
        # for s_pos, e_pos, rangeType in divisional_ranges:
        #     Thread(target=py.uploadFileServlet, args=(redirectionUrl, s_pos, e_pos, length, uploadTaskID, Root / filename, rangeType,)).start()
        # time.sleep(1)
        print(filename, "上传成功")
    else:
        print("秒传完成")


if __name__ == '__main__':
    main()
