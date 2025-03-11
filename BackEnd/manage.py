#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-07-27 23:15
# Author:  rongli
# Email:   abc@xyz.com
# File:    manager.py
# Project: fa-demo
# IDE:     PyCharm
import os
import uvicorn
from backend.config import settings


if __name__ == "__main__":
    # 获取日志配置文件的路径
    project_env = 'prod' if os.getenv('PROJECT_ENV') == 'prod' else 'dev'
    log_config_path = str(settings.base_dir / 'backend' / 'config' / f'logging.{project_env}.json')
    uvicorn.run(
            app='backend.server:app',
            host=settings.server_host,
            port=settings.server_port,
            reload=settings.debug,
            reload_dirs=["backend"],
            log_config=log_config_path,
            use_colors=True
    )
    # uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, debug=True, workers=2, use_colors=True)
