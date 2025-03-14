# -*- coding: utf-8 -*-
# @Time    : 2023/3/27
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : iptools.py
# @Software: PyCharm
import json

import requests


def get_ip():
    """
    爬取的IP池地址
    :return:
    """
    # 删除数据库内容
    print("运行等待20秒，请耐心等待")
    # 获取网站数据
    url = 'https://uu-proxy.com/api/free'
    try:

        strhtml = requests.get(url, verify=False)
        data = json.loads(strhtml.text)
        for i in range(len(data['free']['proxies'])):
            # 下面是 地址、端口号、协议、支持HTTPS
            ip = data['free']['proxies'][i]['ip']
            port = data['free']['proxies'][i]['port']
            protocol = data['free']['proxies'][i]['scheme']
            country = "CN"
            # 添加的数据库
            print(ip + ':' + str(port), ip, port, protocol, country)
        # 关闭爬取网站
        strhtml.close()

    except Exception as e:
        print("异常提示,ip_pool>get_ip: " + str(e))


def main():
    get_ip()


if __name__ == '__main__':
    main()
