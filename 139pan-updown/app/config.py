# -*- coding: utf-8 -*-
# @Time    : 2022/11/12
# @Author  : Naihe
# @File    : config.py
# @Software: PyCharm
import platform
from os import getenv
from pathlib import Path

B = 1024
M = B * B
G = M * B

Root = Path(__file__).parent.parent
STATIC_ROOT = Root / "app/assets"
CHUNK_SIZE = 2 ** 16
SLICE_SIZE = M * 20
AccessToken = getenv(
    "AccessToken") or ""

parentCatalogID = ""  # 路径
USER = getenv("USER") or 1
IP = "0.0.0.0"
PORT = 8080
url_regex = r"(?:http|https)://((?:[\w-]+\.)+[a-z0-9]+)((?:\/[^/?#]*)+)?(\?[^#]+)?(#.+)?"

RPC_URL = getenv("RPC_URL") or "http://x:6800/jsonrpc"
RPC_TOKEN = getenv("RPC_TOKEN") or "x"

try:
    import asyncio
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvloop.install()
except ImportError:
    pass

if "Windows" in platform.platform():
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
