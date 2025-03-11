# -*- coding: utf-8 -*-
# @Time    : 2023/1/4
# @Author  : Naihe
# @File    : tscache.py
# @Software: PyCharm
import zlib
import diskcache
from aiocache.plugins import BasePlugin
from aiocache.serializers import BaseSerializer

from backend.config import settings


class MyCustomPlugin(BasePlugin):
    async def pre_add(self, *args, **kwargs):
        pass

    async def post_add(self, *args, **kwargs):
        pass

    async def pre_set(self, *args, **kwargs):
        pass

    async def post_set(self, *args, **kwargs):
        pass

    async def pre_delete(self, *args, **kwargs):
        pass

    async def post_delete(self, *args, **kwargs):
        pass

    async def post_expire(self, *args, **kwargs):
        pass

    async def pre_expire(self, *args, **kwargs):
        pass


class CompressionSerializer(BaseSerializer):
    DEFAULT_ENCODING = None

    def dumps(self, value):
        if isinstance(value, bytes):
            compressed = zlib.compress(value)
        else:
            compressed = zlib.compress(value.encode())
        return compressed

    def loads(self, value):
        if isinstance(value, bytes):
            decompressed = zlib.decompress(value)
        else:
            decompressed = value if not value else zlib.decompress(value).decode()
        return decompressed


class TScache(object):
    def __init__(self, direct='temp'):
        self.dcache = diskcache.Cache(direct)
        # _cache = Cache(r"D:/my_cache",
        #                  shards=64,  # 将缓存文件自动分成64个部分
        #                  timeout=1,
        #                  size_limit=3e11,  # 每个部分文件的文件最大占用空间
        #                  disk_min_file_size=2**20,     # 文件最小尺寸
        #                  )
        # self._cache: Dict[str, object] = {}

    def get(self, key, default=None, loads_fn=None, namespace=None, _conn=None):
        return self.dcache.get(key, default=default, retry=True)

    def set(self, key, value, ttl=None, dumps_fn=None, namespace=None, _cas_token=None, _conn=None):
        return self.dcache.set(key, value, expire=ttl or 1, retry=True)


cache = TScache(settings.base_dir / "temp")


