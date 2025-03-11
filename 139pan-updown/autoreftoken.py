# -*- coding: utf-8 -*-
# @Time    : 2022/12/22
# @Author  : Naihe
# @File    : autoreftoken.py
# @Software: PyCharm
import re
import time
from base64 import b64encode, b64decode
import requests


def main():
    url = "https://aas.caiyun.feixin.10086.cn:443/tellin/authTokenRefresh.do"   # 针对即将过期token刷新时长
    AccessToken = ""
    headers = {
        'Host': 'aas.caiyun.feixin.10086.cn:443',
        'Accept': 'text/javascript',
        'Authorization': 'Basic ' + AccessToken,
        'Connection': 'keep-alive',
        'Content-Type': 'application/xml; charset=utf-8',
        "x-DeviceInfo": "",
        "x-MM-Source": "001",
        "x-deviceID": "",
        'x-huawei-channelSrc': '10200153',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,en,*',
        'User-Agent': 'Mozilla/5.0',
        "x-ExpRoute-Code": "routeCode=,type=2",
    }
    _data = b64decode(AccessToken).decode("utf-8").split(":")
    token = _data.pop()
    data = f'<?xml version="1.0" encoding="utf-8"?><root><token>{token}</token><account>{_data[-1]}</account><clienttype>656</clienttype></root>'
    with requests.post(url=url, headers=headers, data=data) as res:
        if "not exist or has expired" not in res.text:
            new_token = re.findall(r"<token>(.*?)</token>", res.text)[0]
            _data.append(new_token)
            new_AccessToken = b64encode(":".join(_data).encode("utf-8")).decode("utf-8")
            print(new_AccessToken)


if __name__ == '__main__':
    main()
