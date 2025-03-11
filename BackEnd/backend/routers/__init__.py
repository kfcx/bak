#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-07-27 20:30
# Author:  rongli
# Email:   abc@xyz.com
# File:    __init__.py.py
# Project: fa-demo
# IDE:     PyCharm
from fastapi import APIRouter
from .access import router as access_router
from .account import router as account_router
from .channel import router as channel_router
from .proxy import router as proxy_router
from .monitor import router as monitor_router
from .docs import custom_docs as custom_docs
from .role import router as role_router
from .user import router as user_router
from ..config import settings

api_routers = APIRouter(prefix=settings.url_prefix)

api_routers.include_router(account_router)  # 用户中心
api_routers.include_router(user_router)  # 用户管理
api_routers.include_router(role_router)  # 角色管理
api_routers.include_router(access_router)  # 权限管理
api_routers.include_router(channel_router)  # 频道管理
api_routers.include_router(proxy_router)  # 代理模块
api_routers.include_router(monitor_router)  # 系统管理
