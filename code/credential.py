# -*- coding: utf-8 -*-
# @Time    : 2023/3/18
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : credential.py
# @Software: PyCharm
import asyncio

import aiofiles
import aiohttp
import json


async def scrape():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://poe.com/login') as pb:
            pbCookie = pb.headers.get("set-cookie").split(";")[0]
        async with session.get('https://poe.com/api/settings', headers={'cookie': pbCookie}) as setting:
            if setting.status != 200:
                raise Exception("Failed to fetch token")
            appSettings = json.loads(await setting.text())
            channelName = appSettings['tchannelData']['channel']
    return {
        'pbCookie': pbCookie,
        'channelName': channelName,
        'appSettings': appSettings,
    }


async def getUpdatedSettings(channelName, pbCookie):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://poe.com/api/settings?channel={channelName}', headers={'cookie': pbCookie}) as setting:
            if setting.status != 200:
                raise Exception("Failed to fetch token")
            appSettings = json.loads(await setting.text())
            minSeq = appSettings['tchannelData']['minSeq']
        async with aiofiles.open("config.json", mode='r') as file:
            credentials = json.loads(await file.read())
        credentials['app_settings']['tchannelData']['minSeq'] = minSeq
        async with aiofiles.open("config.json", mode='w') as file:
            await file.write(json.dumps(credentials, indent=4))
    return {
        'minSeq': minSeq,
    }


async def main():
    data = await scrape()
    print("---------------")
    print(data)
    print("---------------")
    data = await getUpdatedSettings(data["channelName"], data["pbCookie"])
    print(data)


if __name__ == '__main__':
    # asyncio.run(main())
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())