# -*- coding: utf-8 -*-
# @Time    : 2022/11/12
# @Author  : Naihe
# @File    : utile.py
# @Software: PyCharm
import hashlib
import asyncio
import time
import aiofiles
import aiofiles.os
from itertools import count

import aiohttp
import requests
from aiohttp.multipart import BodyPartReader
from loguru import logger

from app.upload import calc_up_range
from app.config import CHUNK_SIZE, RPC_URL, RPC_TOKEN


async def addUri(uri, dir_name, file_name):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    }
    # options = {"dir": dir_name, "out": file_name}
    options = {"out": file_name}
    data = {"jsonrpc": "2.0", "method": "aria2.addUri", "id": "",
            "params": [f"token:{RPC_TOKEN}", [uri], options]}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=RPC_URL, headers=headers, json=data) as res:
            return await res.text()


async def callback(file, url):
    try:
        with requests.head(url=url, headers={
            "Accept": "*/*",
            "Referer": "https://www.bilibili.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
        }, timeout=5) as res:
            filesize = int(res.headers.get("Content-Length") or 0)
            if filesize == 0 or res.headers.get("Accept-Ranges") != "bytes":
                logger.warning(f"{file.name} 不支持分块下载")
                flag = False
            else:
                flag = True
    except requests.exceptions.ReadTimeout as e:
        logger.error(e)
        flag = False

    if file.is_file() and filesize == file.stat().st_size:
        logger.info(f"读取本地缓存 {filesize}")
        hmd5, length = await read_file(file)
    else:
        logger.info(f"开始下载 {file.name}")
        sem = asyncio.Semaphore(5)
        try:
            assert flag
            divisional_ranges = calc_up_range(filesize)
            tasks = [get_request_async(sem, url, file, s_pos, e_pos)
                     for s_pos, e_pos, rangeType, sleep in divisional_ranges]
            # loop.run_until_complete(asyncio.wait(tasks))
            await asyncio.gather(*tasks)
            hmd5 = hashlib.md5((str(time.time()) + file.name).encode()).hexdigest()
            length = round(file.stat().st_size)
        except Exception as e:
            print("切换单线程下载", e)
            hmd5, length = await get_request(url, file)

        logger.info("结束下载")

    logger.info(f"{file.name}, {hmd5}, {length}")
    return file, hmd5, length


async def get_request_async(sem, url, filename, s_pos, e_pos):
    headers = {
        "Accept": "*/*",
        'Connection': 'Keep-Alive',
        'Range': f'bytes={s_pos}-{e_pos}',
        "Upgrade": "http/1.1",
        "Referer": "https://www.bilibili.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
    }
    md5 = hashlib.md5()
    length = 0
    async with sem:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as res:
                logger.info("{} status:{}".format(filename.name, res.status))
                async with aiofiles.open(filename, "wb") as f:
                    await f.seek(s_pos)
                    async for chunk in res.content.iter_chunked(CHUNK_SIZE):
                        md5.update(chunk)
                        length += len(chunk)
                        await asyncio.sleep(0)
                        await f.write(chunk)
                return md5.hexdigest(), length


async def get_request(url, filename):
    headers = {
        "Accept": "*/*",
        'Connection': 'Keep-Alive',
        "Upgrade": "http/1.1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
    }
    md5 = hashlib.md5()
    length = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as res:
            logger.info("{} status:{}".format(filename.name, res.status))
            async with aiofiles.open(filename, "wb") as f:
                async for chunk in res.content.iter_chunked(CHUNK_SIZE):
                    md5.update(chunk)
                    length += len(chunk)
                    await f.write(chunk)
                return md5.hexdigest(), length


async def write_file(field: BodyPartReader, filename: str):
    """Write a file to disk."""
    md5 = hashlib.md5()
    length = 0
    async with aiofiles.open(filename, "wb") as f:
        while chunk := await field.read_chunk(size=CHUNK_SIZE):
            md5.update(chunk)
            length += len(chunk)
            await f.write(chunk)
    return md5.hexdigest(), length


async def read_file(filename):
    """read a file to disk."""
    if filename.stat().st_size > 104857600 * 2:
        hmd5 = hashlib.md5((str(time.time()) + filename.name).encode()).hexdigest()
    else:
        md5 = hashlib.md5()
        async with aiofiles.open(filename, "rb") as f:
            while chunk := await f.read(CHUNK_SIZE):
                md5.update(chunk)
        hmd5 = md5.hexdigest()
    length = filename.stat().st_size
    return hmd5, length


async def unique_filename(original_path: str):
    """Return a unique filename."""
    if not await aiofiles.os.path.exists(original_path):
        return original_path

    split = original_path.rsplit(".", 1)
    base = split[0]
    ext = "." + split[1] if len(split) > 1 else ""

    for i in count(1):
        path = f"{base}({i}){ext}"
        if not await aiofiles.os.path.exists(path):
            return path


def done_callback(futu):
    print('Done')
    print(futu.result())


if __name__ == '__main__':
    import asyncio
    from pathlib import Path

    url = "https://vdn1.vzuu.com/HD/e898cfec-ccf3-11eb-b43a-6ec658071f3e-t1111-vgodrDABRC.mp4?disable_local_cache=1&auth_key=1629718189-0-0-2e4eceee29e2d17a92c77fd49911d39a&f=mp4&bu=http-com&expiration=1629718189&v=hw"
    url = "https://cn-ahhn-cm-01-05.bilivideo.com/upgcxcode/75/46/889994675/889994675-1-208.mp4?e=ig8euxZM2rNcNbNBhWdVhwdlhbU1hwdVhoNvNC8BqJIzNbfq9rVEuxTEnE8L5F6VnEsSTx0vkX8fqJeYTj_lta53NCM=&uipk=5&nbs=1&deadline=1668619923&gen=playurlv2&os=bcache&oi=3748179511&trid=0000f194c6494a4e4cbfbfc00ce7962513b7T&mid=0&platform=html5&upsig=cdb32508211b1d35b8d7bbf6406a47bc&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=10102&bvc=vod&nettype=0&bw=251235&orderid=0,1&logo=80000000"
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logger.info("开始")
    loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(asyncio.ProactorEventLoop())
    # asyncio.set_event_loop(asyncio.new_event_loop())
    # asyncio.run(get_request(url, Path("dem2o.mp4")))
    try:
        sem = asyncio.Semaphore(5)
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
        }
        with requests.head(url=url, headers=headers) as res:
            filesize = int(res.headers['Content-Length'])
            print(filesize)
        divisional_ranges = calc_up_range(filesize)
        tasks = asyncio.gather(*[get_request_async(sem, url, Path("ddd.mp4"), s_pos, e_pos)
                                 for s_pos, e_pos, rangeType, sleep in divisional_ranges])
        tasks.add_done_callback(done_callback)
        feature = asyncio.ensure_future(asyncio.gather(*tasks))
        loop.run_until_complete(feature)
        loop.close()
    except Exception as e:
        print(e)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(get_request(url, Path("ddd.mp4")))
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(get_request_async(sem, url, Path("assets/xxx.mp4"), 0, ""))
    logger.info("结束")
