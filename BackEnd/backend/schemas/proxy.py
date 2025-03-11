# -*- coding: utf-8 -*-
# @Time    : 2023/3/28
# @Author  : Naihe
# @File    : proxy.py
# @Software: PyCharm
from typing import Optional
from pydantic import BaseModel, Field, validator

from ..config import settings


class ProxyM3u8(BaseModel):
    url: Optional[str] = Field(..., regex=settings.url_regex, description='频道地址')

    @validator('url')
    def url_match(cls, value, ):
        return value


class ProxyTS(BaseModel):
    x: Optional[str] = Field(..., min_length=18, description='ts索引')


