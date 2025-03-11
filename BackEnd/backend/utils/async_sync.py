#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-08-22 00:08
# Author:  rongli
# Email:   abc@xyz.com
# File:    run_sync.py
# Project: fa-demo
# IDE:     PyCharm

import asyncio
import functools
from typing import Callable, Coroutine

from starlette.concurrency import run_in_threadpool
from tortoise import Tortoise

from ..config import settings

# 同步->异步 | 异步->同步
# https://blog.csdn.net/Android_boom/article/details/125000166
# from asgiref.sync import async_to_sync, sync_to_async
# import asyncer


def sync_to_async(func: Callable):
    """ 把同步任务转为异步的线程去执行 此处借用了 run_in_threadpool，经大佬提醒此方法的实际并发量可能受到线程池的限制！！！ """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_ret = await run_in_threadpool(func, *args, **kwargs)
        return func_ret

    return wrapper


def async_to_sync(f: Callable[..., Coroutine]):
    """ 把异步转为同步 """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(f(*args, **kwargs))
        else:
            loop.run_until_complete(f(*args, **kwargs))

    return wrapper


def tortoise_wrapper(f: Callable):
    """ 包一层 tortoise 的 init 的 close_connections """

    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        await Tortoise.init(settings.tortoise_orm_config)
        try:
            await f(*args, **kwargs)
        finally:
            print("关闭mysql连接")
            await Tortoise.close_connections()

    return wrapper


def cli_wrapper(f: Callable):
    """    manage命令的装饰器    """
    return async_to_sync(tortoise_wrapper(f))
