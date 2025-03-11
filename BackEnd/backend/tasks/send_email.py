#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-07-28 22:11
# Author:  rongli
# Email:   abc@xyz.com
# File:    send_email.py
# Project: fa-demo
# IDE:     PyCharm
import asyncio
import yagmail


async def send_email(account, captcha):
    yag = yagmail.SMTP(user="@qq.com", password="", host='smtp.qq.com')
    contents = [
        '你的验证码是：{}'.format(captcha),
        '请勿泄露给他人',
        '验证码有效期30分钟'
    ]
    yag.send(account, 'HLS流媒体代理系统', contents)

    print(account, '-->', captcha)
    return


if __name__ == '__main__':
    asyncio.run(send_email('@qq.com', '123456'))
