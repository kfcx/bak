from pprint import pprint
import time

import requests


def sosuo(name):
    url = 'https://api.weipan.cn/2/share/searchNew?platform=ios&page=1&query=' + str(
        name) + '&need_ext=read%2Cvideo_mp4%2Caudio_mp3%2Carchive&sort_order=count_download&page_size=10'
    t = time.time()
    print(t)
    heades = {
        "Accept-Encoding": "gzip",
        "Authorization": 'Weibo {"sign":"6v/AU4PWEu","appkey":"1760281982","access_token":"2.00OKpGeGj8YrMD84afa7c1390s1YrV","expires":"1594368582"}'.replace(
            '123', str(int(t))),
        "Connection": "close",
        "Host": "api.weipan.cn",
        "User-Agent": "VDiskMobile 3.7.7 rv:520 (iPhone; iOS 13.5.1; zh_CN) ChannelID/001",
        "x-vdisk-device-uuid": "32566B45-1B61-45F4-AF01-984F0CC839E8",
    }
    requests.packages.urllib3.disable_warnings()
    with requests.get(url=url, headers=heades, verify=False) as x:
        x1 = x.json()
        x.close()
    return x1


def leibie(num):
    url = 'https://api.weipan.cn/2/share/list?platform=ios&page=1&need_ext=read%2Cvideo_mp4%2Caudio_mp3%2Carchive&category_id=' + str(
        num) + '&table=5&page_size=50'
    t = time.time()
    # print(t)
    heades = {
        "Accept-Encoding": "gzip",
        "Authorization": 'Weibo {"sign":"isZq1pm // k","appkey":"1760281982","access_token":"2.00OKpGeGj8YrMD84afa7c1390s1YrV","expires":"1597048291"}',
        "Connection": "close",
        "Host": "api.weipan.cn",
        "User-Agent": "VDiskMobile 3.7.7 rv:520 (iPhone; iOS 13.5.1; zh_CN) ChannelID/001",
        "x-vdisk-device-uuid": "32566B45-1B61-45F4-AF01-984F0CC839E8",
    }
    # if num == 20:
    requests.packages.urllib3.disable_warnings()
    x = requests.get(url=url, headers=heades, verify=False).json()
    return x


def remen():
    url = 'https://api.weipan.cn/2/share/list?platform=ios&page=1&need_ext=read%2Cvideo_mp4%2Caudio_mp3%2Carchive&table=5&page_size=50'
    t = time.time()
    print(t)
    heades = {
        "Accept-Encoding": "gzip",
        "Authorization": 'Weibo {"sign":"6v/AU4PWEu","appkey":"1760281982","access_token":"2.00OKpGeGj8YrMD84afa7c1390s1YrV","expires":"1597045807"}'.replace(
            '123', str(int(t))),
        "Connection": "close",
        "Host": "api.weipan.cn",
        "User-Agent": "VDiskMobile 3.7.7 rv:520 (iPhone; iOS 13.5.1; zh_CN) ChannelID/001",
        "x-vdisk-device-uuid": "32566B45-1B61-45F4-AF01-984F0CC839E8",
    }
    d = eval(heades['Authorization'][6:])
    print(d)
    print(d['expires'])
    print(type(d['expires']))
    # if num == 20:
    requests.packages.urllib3.disable_warnings()
    x = requests.get(url=url, headers=heades, verify=False).json()
    return x


# 0 吉他教学 | 1 高等教育 | 2 个人文书 | 3 文学/小说 | 4 经管营销 | 5 常用软件
# 6 高等教育 |
# | 20 生活百科 |
# so = sosuo('数学建模')  # 关键字搜索
# pprint(so)
# print(len(so))
# exit()

print(remen())
# a = {"Accept-Encoding": "gzip",
#       "Authorization": "Weibo {"sign":"msv59qssou","appkey":"1760281982","access_token":"2.00OKpGeGj8YrMD84afa7c1390s1YrV","expires":"1597048291
#      "}", "Connection": "close",
#      "Host": "api.weipan.cn",
#      "User-Agent": "VDiskMobile 3.7.7 rv:520 (iPhone; iOS 13.5.1; zh_CN) ChannelID/001",
#      "x-vdisk-device-uuid": "32566B45-1B61-45F4-AF01-984F0CC839E8", }
# n = 20
# pprint(leibie(n))
# with open(str(n) + '.txt', 'a+', encoding='utf-8') as f:
#     f.write(a)
#     f.close()
# pformat
