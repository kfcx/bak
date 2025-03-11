#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-07-27 22:14
# Author:  rongli
# Email:   abc@xyz.com
# File:    user.py
# Project: fa-demo
# IDE:     PyCharm
from fastapi import Request
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from pydantic import validator
from tortoise import fields

from .abc import TortoiseBaseModel, AccessBaseModel
from ..enums import OperationMethod, OperationObject, UserGender
from ..enums.model import MenuType


class Channel(TortoiseBaseModel):
    """
    频道
    """
    hash_id: str = fields.CharField(unique=True, max_length=16, description="散列url唯一id")
    tvg_id: str = fields.CharField(null=True, max_length=100, description="tvg_id")
    tvg_country: str = fields.CharField(null=True, max_length=50, description="国家")
    tvg_language: str = fields.CharField(null=True, max_length=20, description="语言")
    tvg_logo: str = fields.CharField(null=True, max_length=255, description="tvg_logo")
    group_title: str = fields.CharField(null=True, max_length=50, description="分组")
    title = fields.CharField(max_length=255, description="频道标题")
    url = fields.CharField(max_length=255, description="资源URL")
    description = fields.CharField(null=True, max_length=255, description="描述")
    role: fields.ManyToManyRelation["Role"] = fields.ManyToManyField("base.Role", related_name="channel",
                                                                     on_delete=fields.CASCADE)

    class Meta:
        table_description = "频道表"
        table = "channel"

    def __str__(self):
        return f"<{self.__class__.__name__} username: {self.hash_id}>"

    @property
    def role_list(self):
        return list(self.role)

    @property
    def role_values(self):
        return [role.pk for role in self.role if role.status]


class User(TortoiseBaseModel):
    """
    用户
    """
    username = fields.CharField(unique=True, max_length=20, description="用户名")
    password = fields.CharField(max_length=255, description="密码")
    nickname = fields.CharField(null=True, max_length=255, description='昵称')
    email = fields.CharField(unique=True, null=True, max_length=255, description='邮箱')
    full_name = fields.CharField(null=True, max_length=255, description='姓名')
    is_superuser = fields.BooleanField(default=False, description='是否为超级管理员')
    head_img = fields.CharField(null=True, max_length=255, description='头像')
    gender = fields.IntEnumField(UserGender, default=UserGender.unknown)
    role: fields.ManyToManyRelation["Role"] = fields.ManyToManyField("base.Role", related_name="user",
                                                                     on_delete=fields.CASCADE)
    profile: fields.OneToOneRelation["UserProfile"]

    class Meta:
        table_description = "用户表"
        table = "user"

    def __str__(self):
        return f"<{self.__class__.__name__} username: {self.username}>"

    def check_password(self, raw_password: str) -> bool:
        """
        验证密码
        :param raw_password: 明文密码
        :return: 检验通过返回 True, 失败返回 False
        """
        return pbkdf2_sha256.verify(raw_password, self.password)

    async def set_password(self, raw_password: str) -> None:
        """
        加密用户密码
        :param raw_password: 明文密码
        :return: None
        """
        self.password = pbkdf2_sha256.hash(raw_password)
        await self.save()

    # @property
    # def phone_number(self) -> str | None:
    #     """ 手机号脱敏 """
    #     if self.phone is None:
    #         return None
    #     return f"{self.phone[:3]}****{self.phone[-4:]}"

    @property
    def role_list(self):
        return list(self.role)

    @property
    def role_values(self):
        return [role.pk for role in self.role if role.status]


class Role(TortoiseBaseModel):
    user: fields.ManyToManyRelation["User"]
    role_name = fields.CharField(max_length=15, description="角色名称")
    order_no = fields.IntField(default=999, null=True, description='用来排序的序号')
    access: fields.ManyToManyRelation["Access"] = fields.ManyToManyField("base.Access", related_name="role_menu",
                                                                         on_delete=fields.CASCADE)
    channels: fields.ManyToManyRelation["Channel"] = fields.ManyToManyField("base.Channel", related_name="role_channel",
                                                                            on_delete=fields.CASCADE)

    class Meta:
        table_description = "角色表"
        table = "role"

    @property
    def menu_values(self):
        return [access.pk for access in self.access]

    @property
    def channels_values(self):
        return [channels.pk for channels in self.channels]


# class Access(TortoiseBaseModel):
#     role: fields.ManyToManyRelation[Role]
#     # 前端动态生成菜单需要的参数
#     path = fields.CharField(null=True, max_length=255, description="路径")
#     name = fields.CharField(unique=True, max_length=255, description="名称")
#     component = fields.CharField(null=True, max_length=255, description='组件')
#     redirect = fields.CharField(null=True, max_length=255, description='重定向')
#     # RouteMeta
#     title = fields.CharField(unique=True, max_length=255, description="标题")
#     icon = fields.CharField(null=True, max_length=255, description="图标")
#     hide_children_in_menu = fields.BooleanField(default=False, description="隐藏所有子菜单")
#     hide_menu = fields.BooleanField(default=False, description="当前路由不再菜单显示")
#
#     is_router = fields.BooleanField(default=True, description="是否为前端路由")
#     is_button = fields.BooleanField(default=False, description="是否为按钮")
#     scopes = fields.CharField(null=True, unique=True, max_length=255, description='权限范围标识')
#     parent_id = fields.IntField(default=0, description='父id')
#
#     order_no = fields.IntField(default=999, null=True, description='用来排序的序号')
#
#     class Meta:
#         table_description = "权限表"
#         table = "access"
#
#    @validator('path')
#    def passwords_match(cls, value, ):
#        print(value)
#        return cls.component  # 截断长度超过50的部分
#
#    def __str__(self):
#        return f"<Access {self.title} {self.scopes}>"


class Access(AccessBaseModel):
    """
    菜单
    """
    role: fields.ManyToManyRelation[Role]
    # id = fields.BigIntField(unique=True, description="菜单名")
    title = fields.CharField(max_length=255, description="菜单名称")
    component = fields.CharField(max_length=255, description="菜单组件")
    # parent_id = fields.BigIntField(default=0, description="父菜单id")
    parent = fields.ForeignKeyField('base.Access', default=0, null=True, related_name='children')
    type: MenuType = fields.IntField(default=0, description="菜单类型")
    scopes = fields.CharField(null=True, max_length=255, description="权限")
    icon = fields.CharField(null=True, max_length=255, description="菜单图标")
    order_no = fields.IntField(default=1, description="排序")
    redirect = fields.CharField(null=True, max_length=255, description="重定向地址")

    class Meta:
        table_description = "权限表"
        table = "access"

    def __str__(self):
        return f"<Access {self.title} {self.scopes}>"


class UserProfile(TortoiseBaseModel):
    user: fields.OneToOneRelation[User] = fields.OneToOneField('base.User', related_name='profile')
    point = fields.IntField(default=0, description='积分')

    class Meta:
        table_description = "用户扩展资料"
        table = "profile"


class OperationLog(TortoiseBaseModel):
    user_id = fields.IntField(description="用户ID")
    object_cls = fields.CharField(max_length=255, description="操作对象类")
    method = fields.CharField(max_length=255, description="操作方法")
    ip = fields.CharField(null=True, max_length=255, description="访问IP")
    detail = fields.JSONField(description="详细参数")
    remark = fields.CharField(null=True, max_length=255, description="备注")

    @classmethod
    async def add_log(cls, req: Request, user_id: int, object_cls: OperationObject,
                      method: OperationMethod, remark: str):
        # 正确获取ip
        if req.headers.get('x-forwarded-for'):
            ip = req.headers.get('x-forwarded-for')
        else:
            ip = req.scope['client'][0]
        # 密码 显示 为 *
        try:
            body = await req.json()
            for key, value in body.items():
                if "password" in key:
                    body[key] = "*" * len(value)
        except Exception as e:
            body = bytes(await req.body()).decode()

        data = {
            "user_id": user_id,
            "object_cls": object_cls.value,
            "method": method.value,
            "ip": ip,
            "remark": remark,
            "detail": {
                "target_url": req.get("path"),
                "user_agent": req.headers.get('user-agent'),
                "method": req.method,
                "params": dict(req.query_params),
                "body": body
            },
        }
        await cls.create(**data)
