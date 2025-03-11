# -*- coding: utf-8 -*-
# @Time    : 2023/1/12
# @Author  : Naihe
# @File    : cache_tools.py
# @Software: PyCharm
import asyncio
import re
import aiohttp
import itertools
from loguru import logger
from collections import deque
from urllib.parse import urljoin, quote_plus
from backend.decorators.local_cache import cache
from backend.utils.tools import md5, now_time, is_url

vbuffer = 3 
ts_ttl = 2 ** 7  
ts_cache_deque = 2 ** 6 
m3u8_ttl = 2 ** 5 
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
}
cache_info = {
    "m3u8": {},  
    "ts": {},  
    "downloading_count": 0,  
    "downloaded_count": 0,  
    "files_total": 0, 
}


async def processing(url, url_hash, data, urlpath, get_count, background_tasks):
    first_flag = now_time() - cache_info["m3u8"][url_hash]["ts_lastime"] <= vbuffer * 20 
    get_count = 1 if get_count > 1 and not first_flag else get_count
    first = True
    count = 0
    for _ts_url in data: 
        if ".ts" in _ts_url:
            if not is_url(_ts_url):
                _ts_url = urljoin(url, _ts_url)
            ts_hash = md5(_ts_url)
            if ts_hash not in cache_info["ts"]:
                cache_info["m3u8"][url_hash]["index"].append(ts_hash) 
                cache_info["ts"].setdefault(ts_hash, {
                    "url": _ts_url,
                    "status": -1,
                    "size": 0,
                    "stime": 0,
                    "etime": 0,
                }) 

            if count < get_count and cache_info["ts"][ts_hash]["status"] == -1:
                background_tasks.add_task(download, url_hash, ts_hash)
            count += 1
            if first_flag:
                yield f"/api/v1/proxy/{urlpath}?x={url_hash}{ts_hash}\n"
            else:
                if first:
                    yield f"/api/v1/proxy/file.ts?x={url_hash}{ts_hash}"
                    first = False
        elif ".m3u8" in _ts_url:
            if not is_url(_ts_url):
                _ts_url = urljoin(url, _ts_url)
            cache_info["m3u8"].setdefault(url_hash, {})
            get_count = 0
            if urlpath == "hit.ts":
                yield f"/api/v1/proxy/cache.m3u8?url={quote_plus(_ts_url)}\n"
            else:
                yield f"/api/v1/proxy/proxy.m3u8?url={quote_plus(_ts_url)}\n"
        else:
            if first:
                yield _ts_url + "\n"


async def back_ts_down(url_hash, ts_hash, get_count, background_tasks):
    _index = cache_info["m3u8"][url_hash]["index"].index(ts_hash) + 1 
    _temp = 1
    for i, ts_hash in enumerate(
            itertools.islice(tuple(cache_info["m3u8"][url_hash]["index"]), _index, _index + get_count),
            start=1):  # [x: x+vbuffer]
        _temp = i
        if ts_hash in cache_info["ts"] and cache_info["ts"][ts_hash]["status"] != -1:
            continue 
        background_tasks.add_task(download, url_hash, ts_hash)
        await asyncio.sleep(0.3 + i * 0.05)

    if get_count != 1 and _temp == 1: 
        url = cache_info["m3u8"][url_hash]["m3u8_url"]
        _data = await get_m3u8_down(url, url_hash, 1.2).__anext__()
        await processing(url, url_hash, iter(_data.split("\n")), "hit.ts", 2, background_tasks).__anext__()



async def download(url_hash, ts_hash, x="默认"):
    for i in range(10, 0, -1):
        if cache_info["ts"][ts_hash]["status"] != 0:
            break
        await asyncio.sleep(i * 0.1)
    if _temp_ts := cache.get(ts_hash, namespace="ts"):
        logger.info(f"ts采用缓存{ts_hash}")
        return _temp_ts
    cache_info["ts"][ts_hash]["status"] = 0  
    cache_info["ts"][ts_hash]["stime"] = now_time() 
    cache_info["downloading_count"] += 1
    url = cache_info["ts"][ts_hash]["url"]
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=header, verify_ssl=False) as res:
            _data = await res.read()
            cache.set(ts_hash, _data, ts_ttl, namespace="ts") 
            cache_info["ts"][ts_hash]["status"] = 1 
            _size = round(len(_data) / 1048576, 2)  
            cache_info["files_total"] += _size  
            cache_info["ts"][ts_hash]["size"] = _size  
            cache_info["ts"][ts_hash]["etime"] = now_time()  
            cache_info["downloading_count"] -= 1  
            cache_info["downloaded_count"] += 1  
            cache_info["m3u8"][url_hash]["ts_lastime"] = now_time() 
            return _data


async def get_m3u8_down(url, url_hash, x=0.8):
    cache_info["m3u8"].setdefault(url_hash, {
        "duration": 0,
        "m3u8_url": url,
        "ts_lastime": 0,
        "m3u8_lastime": 0,
        "status": -1,
        "index": deque(maxlen=ts_cache_deque)
    })
    for i in range(5, 0, -1):  # 1.2s
        if cache_info["m3u8"][url_hash]["status"] != 0:
            break
        await asyncio.sleep(i * 0.08)

    # if now_time() - cache_info["m3u8"][url_hash]["m3u8_lastime"] < 1: 
    if now_time() - cache_info["m3u8"][url_hash]["m3u8_lastime"] < (
            (cache_info["m3u8"][url_hash]["duration"] * x) or 1): 
        data = cache.get(url_hash, namespace="m3u8")
        yield data
    cache_info["m3u8"][url_hash]["status"] = 0
    async with aiohttp.ClientSession(headers=header) as session:
        # async with session.get(url=url, allow_redirects=True, verify_ssl=False) as res:  
        async with session.get(url=url, allow_redirects=True) as res: 
            if res.status != 200:
                logger.error(f"proxy下载出错 {res.status}, {await res.text()}")
            if (res.content_length or 0) > 1048576 * 10:  # 1M * 10
                logger.error(f"超过大小 {res.content_length}")
                yield "数据超过限制大小"
            cache_info["m3u8"][url_hash]["status"] = 1
            cache_info["m3u8"][url_hash]["m3u8_lastime"] = now_time()
            _data = await res.text()
            cache_info["m3u8"][url_hash]["duration"] = int((re.findall(r"#EXT-X-TARGETDURATION:(\d+)", _data) or [10]).pop())
            cache.set(url_hash, _data, m3u8_ttl, namespace="m3u8")
            yield _data

