# -*- coding: utf-8 -*-
# @Time    : 2023/6/27
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : aaa.py
# @Software: PyCharm
import requests


def main():
    url = "https://chatgpt.vulcanlabs.co/api/v3/chat"
    data = {
        "model": "gpt-4",
        "user": "1688012218.1266088_1CFBCDE9-AB8C-42DA-AC9F-4954A800BDCE",
        "messages": [
            {
                "content": "You are an AI language model called GPT-4, created by OpenAI. GPT-4 is an improved version of ChatGPT.",
                "role": "system"
            },
            {
                "content": "父亲和母亲能结婚吗？",
                "role": "user"
            }
        ]
    }
    header = {
        "User-Agent": "iOS App, Version 5.7.2",
        "Authorization": "Bearer ",
        "Host": "chatgpt.vulcanlabs.co",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Content-Type": "application/json",
    }
    with requests.post(url=url, headers=header, json=data) as res:
        print(res.status_code)
        print(res.text)



if __name__ == '__main__':
    main()
