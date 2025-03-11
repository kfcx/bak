#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-07-30 00:01
# Author:  rongli
# Email:   abc@xyz.com
# File:    account.py
# Project: fa-demo
# IDE:     PyCharm

from typing import Union

from aioredis import Redis
from fastapi import APIRouter, Depends, Request
from simpel_captcha import img_captcha, captcha
from starlette.background import BackgroundTasks
from starlette.responses import StreamingResponse

from ..config import settings
from ..dependencies import (create_access_token, get_captcha_code, get_current_active_user, get_redis)
from ..dependencies.redis import get_email_captcha_code
from ..enums import OperationMethod as OpMethod, OperationObject as OpObject
from ..models import OperationLog, User, Role
from ..schemas import (FailResp, LoginResult, ModifyInfo, ModifyPassword,
                       RoleInfoForLoginResp, SingleResp, SuccessResp, UserInfo,
                       UserLogin, UserRegister)
from ..schemas.user import UserEmail
from ..tasks import send_email

router = APIRouter(prefix='/user', tags=['用户中心'])


@router.post('/register', response_model=Union[SingleResp[UserInfo], FailResp], summary='用户注册')
async def register(post: UserRegister, code_in_redis: str = Depends(get_email_captcha_code)):
    if code_in_redis is None:
        return FailResp(code=10302, msg='验证码已过期')
    if post.code.lower() != code_in_redis:
        return FailResp(code=10303, msg='验证码错误')

    if await User.filter(username=post.username).exists():
        return FailResp(code=10101, msg='当前用户名已被占用')
    user = await User.create(nickname=post.username, **post.dict(exclude_unset=True, exclude_none=True))
    await user.set_password(post.password)
    role = await Role.get(role_name="用户")
    await user.role.add(role)
    user_info = UserInfo.from_orm(user)
    return SingleResp[UserInfo](data=user_info)


@router.get("/captcha", summary='图片验证码')
async def image_captcha(req: Request, redis: Redis = Depends(get_redis)):
    image, text = img_captcha(byte_stream=True)
    session_value = req.session.get(settings.session_cookie_name)
    key = settings.captcha_key.format(session_value)
    print("图片验证码：", text)
    await redis.setex(key, settings.captcha_seconds, text.lower())
    return StreamingResponse(content=image, media_type='image/jpeg')


@router.post("/verify", summary='邮箱验证码')
async def email_captcha(background_tasks: BackgroundTasks, req: Request, post: UserEmail, redis: Redis = Depends(get_redis)):
    if await User.filter(email=post.email).exists():
        return FailResp(code=10101, msg='当前邮箱已注册')
    text = captcha(6)
    session_value = req.session.get(settings.session_cookie_name)
    key = settings.emailCaptcha_key.format(session_value)
    print("邮箱验证码：", text)
    print("邮箱：", post.email)
    background_tasks.add_task(send_email, post.email, text)
    await redis.setex(key, settings.emailCaptcha_seconds, text.lower())
    return SuccessResp(data={"msg": "验证码已发送至邮箱，请注意查收"})


@router.post('/login', response_model=Union[SingleResp[LoginResult], FailResp], summary='用户登陆')
async def login(req: Request, post: UserLogin, code_in_redis: str = Depends(get_captcha_code)):
    if code_in_redis is None:
        return FailResp(code=10302, msg='验证码已过期')
    if post.code.lower() != code_in_redis:
        return FailResp(code=10303, msg='验证码错误')
    user = await User.get_or_none(username=post.username)
    if user is None:
        return FailResp(code=10301, msg='账号不存在')
    if not user.check_password(post.password):
        return FailResp(code=10301, msg='账号与密码不匹配')
    access_token = create_access_token(data={"sub": user.username})

    await OperationLog.add_log(req, user.pk, OpObject.user, OpMethod.login_by_account, f"用户登陆(ID={user.pk})")
    # 此处只是为了配合前端，返回的信息为是否为管理员，没什么实际用处，只是不想改前端代码而已
    role_name = '超级管理员' if user.is_superuser else "普通管理员"
    role_value = '超级管理员' if user.is_superuser else "普通管理员"
    role_info = RoleInfoForLoginResp(role_name=role_name, value=role_value)
    login_result = LoginResult(id=user.pk, token=access_token, role=role_info)

    return SingleResp[LoginResult](data=login_result)


@router.get('', response_model=Union[SingleResp[UserInfo], FailResp], summary='查看个人信息')
async def get_my_info(me=Depends(get_current_active_user)):
    return SingleResp[UserInfo](data=me)


@router.put('', response_model=Union[SingleResp[UserInfo], FailResp], summary='修改个人信息')
async def change_info(req: Request, post: ModifyInfo, me: User = Depends(get_current_active_user)):
    await me.update_from_dict(post.dict(exclude_unset=True, exclude_none=True))
    await me.save()
    await OperationLog.add_log(req, me.pk, OpObject.user, OpMethod.update_object, f"用户修改个人信息({me.pk})")
    user_info = UserInfo.from_orm(me)
    return SingleResp[UserInfo](data=user_info)


@router.get("/logout", response_model=Union[SuccessResp, FailResp], summary='用户登出')
async def logout(req: Request, me: User = Depends(get_current_active_user)):
    await OperationLog.add_log(req, me.pk, OpObject.user, OpMethod.logout_by_account, f"用户登出({me.pk})")
    # print(req.session.clear())
    # print(req.session.pop("captcha", None))
    return SuccessResp()

