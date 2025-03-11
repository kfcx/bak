#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-07-27 21:07
# File:    conf.py
# IDE:     PyCharm
import os
import sys
from pathlib import Path
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        # 环境变量文件
        env_file = ".env.prod" if os.getenv('PROJECT_ENV') == 'prod' else ".env.dev"

    # 环境配置: dev prod
    project_env: str = "dev"

    # debug模式
    debug: bool = True if project_env == 'dev' else False

    # 项目标题
    project_title = 'HLS流媒体代理系统'
    # 项目描述
    project_description = 'HLS流媒体代理系统API后端'
    # 项目版本
    project_version = '1.0.0'

    # url的前缀
    url_prefix: str = "/api/v1"
    # host
    server_host: str = '0.0.0.0'
    # server_host: str = '::'
    server_port: int = 8000

    #  swagger docs 的登陆重定向地址
    swagger_ui_oauth2_redirect_url: str = '/docs/oauth2-redirect'
    # swagger docs 额外配置
    swagger_ui_parameters: dict = {"docExpansion": None}
    # /docs 获取 token 的 url
    oauth2_token_url: str = url_prefix + "/test/auth/token"

    # 项目根目录
    base_dir = Path(__file__).absolute().parent.parent.parent
    # 日志目录
    log_dir = base_dir / 'logs'
    # 静态资源
    static_dir = base_dir / 'static'
    static_url_prefix: str = '/static'
    # 用户上传目录
    media_dir = base_dir / 'media'
    media_url_prefix: str = '/media'
    # jinja2 模板目录
    jinja2_templates_dir = base_dir / 'backend' / 'templates'

    # 中间件配置
    # 跨域请求
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["PUT", 'POST', 'GET', 'DELETE', 'OPTIONS']
    cors_allow_headers: List[str] = ["*"]
    # Session
    session_secret_key = "409F301D988909666"
    session_cookie = "session_id"
    session_max_age = 14 * 24 * 60 * 60
    # SetSessionMiddleware
    session_cookie_name = 'session'
    # 日志中间件的白名单，只填写去除 url_prefix 的部分
    logger_path_white_list: List[str] = ['/user/captcha', '/test/files', '/test/uploadfile']
    # TrustedHostMiddleware
    allowed_hosts = ["*"]

    # 数据库
    mysql_host: str = "16"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "x"
    mysql_database: str = "x"

    cache_redis_url: str = "redis://localhost:6379/0"

    # captcha
    # 图片验证码有效时间
    captcha_seconds: int = 5 * 60
    emailCaptcha_seconds: int = 30 * 60
    # 图片验证码key
    captcha_key: str = 'captcha:{}'
    # 邮箱验证码key
    emailCaptcha_key: str = 'emailCaptcha:{}'

    # jwt加密的盐
    jwt_secret_key: str = "97Eca7b8ba85A56"
    # jwt加密算法
    jwt_algorithm: str = 'HS256'
    # token过期时间，单位：秒
    jwt_exp_seconds: int = 7 * 24 * 60 * 60

    url_regex = r"(http|https|rtmp|rtsp)://((?:[\w-]+\.)+[a-z0-9]+)((?:\/[^/?#]*)+)?(\?[^#]+)?(#.+)?"

    @property
    def tortoise_orm_model_modules(self) -> List[str]:
        return ['aerich.models', 'backend.models']

    @property
    def tortoise_orm_config(self) -> dict:
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "host": self.mysql_host,
                        "port": self.mysql_port,
                        "user": self.mysql_user,
                        "password": self.mysql_password,
                        "database": self.mysql_database,
                    },
                    "pool_pre_ping": True,
                    "pool_recycle": 1800,
                }
            },
            "apps": {
                "base": {
                    "models": self.tortoise_orm_model_modules,
                    "default_connection": "default"
                }
            },
            'use_tz': False,
            'timezone': 'Asia/Shanghai'
        }

    @property
    def loguru_config(self):
        return {
            "handlers": [
                {
                    "sink": sys.stdout,
                    "level": "DEBUG",
                    "format": "<green>{time:YYYY-mm-dd HH:mm:request.SSS}</green> | {thread.name} | "
                              "<level>{level}</level> | "
                              "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                              "<level>{message}</level>"
                },
                {
                    "sink": self.log_dir / 'fastapi.log',
                    "level": "INFO",
                    "rotation": "10 MB",
                    "retention": "1 week",
                    "encoding": 'utf-8',
                    "format": "{time:YYYY-mm-dd HH:mm:request.SSS} | {thread.name} | {level} | "
                              "{module} : {function}:{line} -  {message}"
                },
                {
                    "sink": self.log_dir / 'fastapi-error.log',
                    "serialize": True,
                    "level": 'ERROR',
                    "retention": "1 week",
                    "rotation": "10 MB",
                    "encoding": 'utf-8',
                    "format": "{time:YYYY-mm-dd HH:mm:request.SSS} | {thread.name} | {level} | "
                              "{module} : {function}:{line} -  {message}"
                },
            ],
        }
