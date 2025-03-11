# -*- coding: utf-8 -*-
# @Time    : 2023/3/2
# @Author  : Naihe
# @File    : channel.py
# @Software: PyCharm
from datetime import datetime
from typing import Optional, List
from fastapi import Query
from pydantic import BaseModel, Field, validator

from .base import BaseFilter, ORMModel


# -------------------------------  请求部分  ---------------------------------------------

class ChannelCreate(BaseModel):
    """ 增加频道 """
    hash_id: str = Field(None, description='hash_id')
    tvg_id: Optional[str] = Field(None, description='tvg_id')
    tvg_country: Optional[str] = Field(None, description='tvg_country')
    tvg_language: Optional[str] = Field(None, description='tvg_language')
    tvg_logo: Optional[str] = Field(None, description='tvg_logo')
    group_title: Optional[str] = Field(None, description='group_title')
    title: str = Field(..., description='title')
    url: str = Field(..., description='url')
    description: Optional[str] = Field(None, description='description')
    status: Optional[bool] = Field(True, description='状态')
    roles: Optional[List[int]]

    @validator('description')
    def passwords_match(cls, value, ):
        return value[:50]  # 截断长度超过50的部分


class ChannelUpdate(ORMModel):
    """ 更新频道 """
    hash_id: str = Field(None, description='hash_id')
    tvg_id: Optional[str]
    tvg_country: Optional[str] = Field(None, description='tvg_country')
    tvg_language: Optional[str]
    tvg_logo: Optional[str]
    group_title: Optional[str]
    title: str = Field(..., description='title')
    url: str = Field(..., description='url')
    description: Optional[str]
    status: Optional[bool] = Field(True, description='状态')
    roles: Optional[List[int]]


class ChannelFilter(BaseFilter):
    """ 过滤用户 """
    title__icontains: Optional[str] = Query(None, alias="title", description="頻道模糊匹配")
    hash_id__icontains: Optional[str] = Query(None, alias="hash_id")
    role__icontains: Optional[int] = Query(None, alias="role")
    group_title__icontains: Optional[str] = Query(None, alias="group_title")


# ------------------------------------------------------------------------------------
class ChannelInfo(ORMModel):
    """ 频道信息 """
    id: int = Field(None, description='频道id')
    hash_id: str = Field(..., description='频道hash_id')
    title: str = Field(..., description='频道标题')
    url: str = Field(..., description='频道地址')
    tvg_logo: Optional[str]
    tvg_id: Optional[str]
    tvg_country: Optional[str]
    tvg_language: Optional[str]
    create_time: datetime = Field(...)
    update_time: datetime
    status: bool = Field(...)
    group_title: Optional[str]
    description: Optional[str]
    role_values: List[int] = Field([], description="角色值", alias='roles')

