# -*- coding: utf-8 -*-
# @Time    : 2023/3/25
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : websocketa.py
# @Software: PyCharm
import random

import aiofiles
import json
import asyncio
import sys
import difflib

import websockets


async def getSocketUrl():
    tchRand = str(100000 + int(900000 * random.random()))  # They're surely using 6 digit random number for ws url.
    socketUrl = f"wss://tch{tchRand}.tch.quora.com"
    async with aiofiles.open("config.json", mode='r') as file:
        credentials = json.loads(await file.read())
        appSettings = credentials['app_settings']['tchannelData']
        boxName = appSettings['boxName']
        minSeq = appSettings['minSeq']
        channel = appSettings['channel']
        channelHash = appSettings['channelHash']
        baseHost = appSettings['baseHost']

    ws_domain = f"tch{random.randint(1, 1e6)}"
    query = f'?min_seq={minSeq}&channel={channel}&hash={channelHash}'
    return f"{ws_domain}.tch.{baseHost}", f'wss://{ws_domain}.tch.{baseHost}/up/{boxName}/updates' + query
    # return f"{socketUrl}/up/{boxName}/updates?min_seq={minSeq}&channel={channel}&hash={channelHash}"


async def connectWs():
    host, url = await getSocketUrl()
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-WebSocket-Version': '13',
        'Origin': 'https://poe.com',
        'Sec-WebSocket-Extensions': 'permessage-deflate',
        'Sec-WebSocket-Key': 'kdAAp7PEcJixY8l2ZJX8cQ==',
        'DNT': '1',
        'Connection': 'keep-alive, Upgrade',
        'Sec-Fetch-Dest': 'websocket',
        'Sec-Fetch-Mode': 'websocket',
        'Sec-Fetch-Site': 'cross-site',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade': 'websocket',
    }
    async with websockets.connect(url, extra_headers=headers) as ws:
        print("Connected to websocket")
        return ws


async def disconnectWs(ws):
    await ws.close()
    return True


async def listenWs(ws):
    previousText = ''
    while True:
        data = await ws.recv()
        jsonData = json.loads(data)
        if jsonData['messages'] and len(jsonData['messages']) > 0:
            messages = json.loads(jsonData['messages'][0])
            dataPayload = messages['payload']['data']
            text = dataPayload['messageAdded']['text']
            state = dataPayload['messageAdded']['state']
            if state != 'complete':
                differences = difflib.ndiff(previousText, text)
                result = ''
                for part in differences:
                    if part.startswith('+'):    # 该部分可能有问题
                        # if part[0] == 1:  # added
                        # if part[0] == '+':
                        result += part
                    previousText = text
                    sys.stdout.write(result)
            else:
                return True


async def main():
    ws = await connectWs()
    print(ws)
    await listenWs(ws)
    # try:
    #     await listenWs(ws)
    # except AttributeError as e:
    #     print("Connection closed")
    await disconnectWs(ws)


if __name__ == '__main__':
    asyncio.run(main())
