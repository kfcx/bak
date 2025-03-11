# -*- coding: utf-8 -*-
# @Time    : 2022/11/14
# @Author  : Naihe
# @File    : 断点续传.py
# @Software: PyCharm
import hashlib
import time
import requests
import xml.etree.ElementTree as ET

from loguru import logger
from pathlib import Path


request = requests.session()

# 下载地址
# download.mcloud.139.com  广州移动
# download.mcloud.10086.cn  呼和浩特移动


class distran:
    def __init__(self, AccessToken=None):
        AccessToken = ""
        self.AccessToken = AccessToken
        self.USER = 1
        self.parentCatalogID = "1"

    def first_IUploadAndDownload(self, fname, hmd5, length):
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

    def IUploadAndDownload(self, uploadTaskID, contentID):
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

    def uploadFileServlet(self, url, curlen, endlen, length, uploadtaskID, path):
        """上传文件"""
        headers = {
            'Host': 'upload5.mcloud.139.com',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': str(endlen - curlen),
            'Accept': '*/*',
            'Accept-Encoding': '*',
            'Authorization': 'Basic ' + self.AccessToken,
            'Content-Type': 'application/octet-stream',
            # 'Content-Type': 'text/xml;UTF-8',
            'Range': f'bytes={curlen}-{endlen}',
            'contentSize': str(length),
            'uploadtaskID': uploadtaskID,
            "x-DeviceInfo": "",
            "x-MM-Source": "001",
            "x-deviceID": "",
            'x-huawei-channelSrc': '10200153',
        }
        with open(path, "rb") as f:
            f.seek(curlen)
            with request.post(url=url, headers=headers, data=f.read(endlen - curlen + 1), stream=True) as res:
                print(f"uploadFileServlet: {res.status_code}", res.text)
                print(res.headers)
                # assert res.status_code == 200

    def calc_divisional_range(self, filesize, chuck=10):
        chuck = 2 if chuck < 2 else chuck
        step = filesize // chuck
        arr = list(range(0, filesize, step))
        result = []
        for i in range(len(arr) - 1):
            s_pos, e_pos = arr[i], arr[i + 1] - 1
            result.append([s_pos, e_pos])
        result[-1][-1] = filesize - 1
        return result


def main():
    slice_size = 1024 * 1024*1024*1000
    Root = Path(r"\Downloads")
    filename = "zzz.zip"
    length = round((Root / filename).stat().st_size)
    hmd5 = hashlib.md5((str(time.time()) + filename).encode()).hexdigest()
    py = distran()
    isNeedUpload, redirectionUrl, uploadTaskID, contentID = py.first_IUploadAndDownload(filename, hmd5, length)
    if isNeedUpload:
        x_ = py.calc_divisional_range(length, length//slice_size)
        for i, v in enumerate(x_):
            s, e = v
            # if i < 6:
            #     continue
            logger.info(f"uploading {s} - {e}")
            py.uploadFileServlet(redirectionUrl, s, e, length, uploadTaskID, Root / filename)
            logger.info(f"uploading ok {e-s}")
            py.IUploadAndDownload(uploadTaskID, contentID)
            logger.info("完成一次上传")
        print(filename, "上传成功")
    else:
        print("秒传完成")


if __name__ == '__main__':
    main()

    # py = distran()
    # Root = Path()
    # filename = "text"
    # length = (Root / filename).stat().st_size
    # a = py.calc_divisional_range(length, length // 2)
    # for s, e in a:
    #     with open(Root/filename, "rb+") as f:
    #         f.seek(s)
    #         f.read(e-s+1)
