# -*- coding: utf-8 -*-
# @Time    : 2023/3/28
# @Author  : Naihe
# @File    : proxy.py
# @Software: PyCharm
import asyncio
from aioredis import Redis
from fastapi import APIRouter, Depends, Path, Request, Security
from fastapi.background import BackgroundTasks
from loguru import logger
from starlette.responses import StreamingResponse, FileResponse, Response

from ..config import settings
from ..decorators.local_cache import cache
from ..dependencies import check_permissions, get_redis
from ..schemas import (ProxyM3u8, FailResp, SingleResp, SuccessResp, ProxyTS)
from ..utils.cache_tools import processing, download, get_m3u8_down, cache_info, vbuffer, back_ts_down
from ..utils.tools import hash_url, md5, parse

router = APIRouter(prefix='/proxy', tags=['代理模块'])

active_mode = True
headers2 = {
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Content-Type': 'application/vnd.apple.mpegurl',
    'Expires': '-1',
}
headers = {
    'Content-Type': 'video/MP2T',
    'Cache-Control': 'max-age=600',
    'Accept-Ranges': 'bytes'
}
# https://cdn.theoplayer.com/video/big_buck_bunny/big_buck_bunny.m3u8


@router.get('/cache.m3u8')
async def cache_pro(background_tasks: BackgroundTasks,
                    request: Request,
                    post: ProxyM3u8 = Depends()):
    """
        ## 用途/Usage
        - 缓存代理任意链接
        - 需要体验该接口功能请[联系作者](https://github.com/kfcx/)
    """
    url = dict(request.query_params)
    if url:
        url = parse(url)
        url_hash = md5(url)
        _data = await get_m3u8_down(url, url_hash).__anext__()
        _count = vbuffer if active_mode else 0
        return Response(
            "".join([i async for i in processing(url, url_hash, iter(_data.split("\n")), "hit.ts", _count, background_tasks)]),
            status_code=200, headers=headers2)
        # return StreamingResponse(
        #     processing(url, url_hash, iter(_data.split("\n")), "hit.ts", _count, background_tasks), 200,
        #     headers=headers2)
    return FailResp(data="None")


@router.get('/proxy.m3u8')
async def proxy_pro(background_tasks: BackgroundTasks,
                    request: Request,
                    post: ProxyM3u8 = Depends()):
    """
        ## 用途/Usage
        - 代理任意链接
        - 为防止滥用，代理白名单域名内所有频道
        - 白名单域名：【cctvwbndks.v.kcdnvip.com】
        - https://cctvwbndks.v.kcdnvip.com/cctvwbnd/cctv1_2/index.m3u8?BR=md&region=shanghai
    """
    url = dict(request.query_params)
    if url:
        url = parse(url)
        url_hash = md5(url)
        _data = await get_m3u8_down(url, url_hash).__anext__()
        _count = 1 if active_mode else 0
        return Response(
            "".join([i async for i in processing(url, url_hash, iter(_data.split("\n")), "file.ts", _count, background_tasks)]),
            status_code=200, headers=headers2)
        # return StreamingResponse(
        #     processing(url, url_hash, iter(_data.split("\n")), "file.ts", _count, background_tasks), 200,
        #     headers=headers2)
    return FailResp(data="None")


@router.get('/file.ts')
async def file(request: Request,
               post: ProxyTS = Depends()):
    """
        ## 用途/Usage
        - 下载流视频片
    """
    x = post.x
    long = len(x) // 2
    url_hash, ts_hash = x[:long], x[long:]
    if ts_hash in cache_info["ts"]:
        return Response(content=await download(url_hash, ts_hash, "file.ts"), status_code=200, headers=headers,
                        media_type='video/MP2T')
    else:
        return FailResp(msg="NOT FOUND", code=404)


@router.get('/hit.ts')
async def hit(background_tasks: BackgroundTasks,
              request: Request,
              post: ProxyTS = Depends()):
    """
        ## 用途/Usage
        - 缓存下载流视频片
    """
    x = post.x
    long = len(x) // 2
    url_hash, ts_hash = x[:long], x[long:]
    get_count = vbuffer if active_mode else 0
    background_tasks.add_task(back_ts_down, url_hash, ts_hash, get_count, background_tasks)
    logger.debug('启动后台任务backtasklocal')
    for i in range(1, 10):  # range(1, 10): 4.725   1-i*0.095
        # logger.debug(f"第{i}次尝试获取{ts_hash}")
        if ts_hash in cache_info["ts"] and cache_info["ts"][ts_hash]["status"] == 1:
            logger.info(f'{ts_hash} 获取成功 {cache_info["ts"][ts_hash]["status"]}')
            content = cache.get(ts_hash, namespace="ts")
            return Response(content=content, status_code=200, headers=headers)
        else:
            await asyncio.sleep(1 - i * 0.095)
    logger.info(f"NOT FOUND {ts_hash}")
    return Response(content=await download(url_hash, ts_hash, "file.ts"), status_code=200, headers=headers,
                    media_type='video/MP2T')


@router.get('/program.m3u')
async def program_proxy():
    """
        ## 用途/Usage
        - 代理频道列表
    """
    return FileResponse(settings.static_dir / "assets/channel.m3u")
