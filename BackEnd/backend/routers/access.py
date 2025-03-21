#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Time:    2022-07-30 23:50
# Author:  rongli
# Email:   abc@xyz.com
# File:    access.py
# Project: fa-demo
# IDE:     PyCharm
from aioredis import Redis
from fastapi import APIRouter, Depends, Security
from starlette.requests import Request
from tortoise.queryset import F
from ..decorators import cache
from ..dependencies import (check_permissions, get_current_active_user, get_redis)
from ..enums import OperationMethod as OpMethod, OperationObject as OpObject
from ..enums.model import MenuType
from ..models import Access, User
from ..models.base import OperationLog
from ..schemas import FailResp, MenuUpdate, MultiResp, SuccessResp
from ..schemas.access import MenuCreate
from ..utils import make_tree
from ..utils.hash import snowflake


router = APIRouter(prefix='/access', tags=['权限管理'])


@router.get('/router_tree', summary="获取前端路由")
# @cache("router_tree", ex=24 * 60 * 60)
async def get_router_tree(req: Request, me: User = Depends(get_current_active_user)):
    if me.is_superuser:
        user_menu_ids = await Access.all().values_list('id', flat=True)
    else:
        user_menu_ids = await Access.filter(role_menu__user__id=me.pk).values_list('id', flat=True)

    all_menu_list = [{'id': obj.pk,
                      # 'path': f'/{snowflake.generate_id()}' if obj.type == MenuType.button or obj.type == MenuType.directory else obj.path,
                      'path': f'/{snowflake.generate_id()}' if not obj.redirect else obj.redirect,
                      'name': snowflake.generate_id(),
                      'component': obj.component,
                      'redirect': obj.redirect if obj.type == MenuType.link else None,
                      'order_no': obj.order_no,
                      'meta': {
                          'title': obj.title,
                          'icon': obj.icon,
                          # 'hideChildrenInMenu': obj.type == MenuType.menu,
                          'hideChildrenInMenu': obj.redirect is not None,
                          # 'hideMenu': obj.type == MenuType.button,
                      },
                      'parent_id': obj.parent_id,
                      } for obj in await Access.filter(type__in=[0, 1, 3]).all()]
    result_list = []

    # # all_menu_list 并不能拿到父一级的菜单，所以这里还要修正一下
    # # 这一段写得比较丑陋，以后再改吧
    def get_all_menu(menu_ids):
        if not menu_ids:
            return
        temp = []
        for menu_id in menu_ids:
            for menu_item in all_menu_list:
                if menu_id == menu_item['id']:
                    if menu_item not in result_list:
                        result_list.append(menu_item)
                    if menu_item['parent_id'] != 0:
                        temp.append(menu_item['parent_id'])
        get_all_menu(temp)

    get_all_menu(user_menu_ids)

    result_list.sort(key=lambda x: x['order_no'])
    result_list = make_tree(result_list, key_key='id')
    return SuccessResp(data=result_list)


@router.get('/perm_code', response_model=MultiResp[str], summary='获取权限码')
# @cache("perm_code", ex=24 * 60 * 60)
async def get_perm_code(req: Request, me: User = Depends(get_current_active_user)):
    if me.is_superuser:
        data = await Access.all().filter(scopes__not_isnull=True).values_list('scopes', flat=True)
    else:
        data = await Access.all().filter(role_menu__user__id=me.pk, scopes__not_isnull=True).values_list('scopes', flat=True)
    return MultiResp[str](data=data)


@router.get('/menu/tree', summary="获取菜单树", dependencies=[Security(check_permissions, scopes=["menu_retrieve"])])
async def get_menu_tree(req: Request):
    result = await Access.annotate(key=F('id')).all().order_by('order_no', 'id').values('key', 'title', 'parent_id')
    tree_data = make_tree(result,key_key="key")
    return SuccessResp(data=tree_data)


@router.get('/menu/list', summary="菜单列表", dependencies=[Security(check_permissions, scopes=["menu_retrieve"])])
async def get_menu_list():
    # result = await Access.annotate(key=F('id'), menuName=F('title')).all().order_by('order_no', 'id') \
    #     .values('id', 'key', 'title', 'name', 'icon', 'parent_id', 'scopes', 'path', 'component', 'order_no', 'status', 'hide_children_in_menu',
    #             'create_time')
    result = await Access.annotate(value=F('id'), menuName=F('title')).all().order_by('order_no', 'id') \
        .values('id', 'value', 'title', 'icon', 'parent_id', 'scopes', 'type', 'component', 'order_no', 'status')
    tree_data = make_tree(result)
    return SuccessResp(data=tree_data)


@router.put('/menu/{menu_id}', summary="修改菜单", dependencies=[Security(check_permissions, scopes=["menu_update"])])
async def menu_update(req: Request, menu_id: str, post: MenuUpdate, redis: Redis = Depends(get_redis)):
    menu = await Access.get_or_none(pk=menu_id)
    print(menu)
    if menu is None:
        return FailResp(code=30101, msg='菜单项不存在')
    data = post.dict(exclude_none=True, exclude_unset=True)
    await menu.update_from_dict(data)
    await menu.save()
    # 如果修改不是最底层的菜单，就清一下缓存，
    if await Access.filter(parent_id=menu.pk).exists():
        username_list = await User.filter(role__access__id=menu.pk).values_list('username', flat=True)
        if username_list:
            perm_code_key_list = [f"cache:perm_code:{x}" for x in username_list]
            router_tree_key_list = [f"cache:router_tree:{x}" for x in username_list]
            await redis.delete(*perm_code_key_list, *router_tree_key_list)
    # 超管的也清一下
    username_list = await User.filter(is_superuser=True).values_list('username', flat=True)
    if username_list:
        perm_code_key_list = [f"cache:perm_code:{x}" for x in username_list]
        router_tree_key_list = [f"cache:router_tree:{x}" for x in username_list]
        await redis.delete(*perm_code_key_list, *router_tree_key_list)
    await OperationLog.add_log(req, req.state.user.id, OpObject.menu, OpMethod.update_object, f"修改菜单(ID={menu_id})")
    return SuccessResp(data='修改菜单成功')


@router.get('/menu/{menu_id}', summary="查看菜单详情",
            dependencies=[Security(check_permissions, scopes=["menu_retrieve"])])
async def menu_detail(req: Request, menu_id: str):
    menu = await Access.get_or_none(pk=menu_id)
    if menu is None:
        return FailResp(code=30101, msg='菜单项不存在')
    return SuccessResp(data=menu)


async def delete_menu_with_children(access_id: int) -> None:
    access = await Access.get_or_none(id=access_id).prefetch_related("children")

    if access is None:
        raise Exception("删除菜单失败")

    for child in access.children:
        await delete_menu_with_children(child.id)

    await access.delete()

@router.delete('/menu/{menu_id}', summary="删除菜单", dependencies=[Security(check_permissions, scopes=["menu_delete"])])
async def menu_delete(req: Request, menu_id: str):
    menu = await Access.get_or_none(pk=menu_id)
    if menu is None:
        return FailResp(code=30101, msg='菜单项不存在')
    await delete_menu_with_children(menu_id)
    # # 子菜单未处理删除
    # await menu.filter(pk=menu_id).delete()
    await OperationLog.add_log(req, req.state.user.id, OpObject.role, OpMethod.delete_object, f"删除菜单({menu_id})")
    return SuccessResp(data="删除菜单成功")


@router.post('/menu', summary="创建菜单", dependencies=[Security(check_permissions, scopes=["menu_create"])])
async def menu_create(req: Request, post: MenuCreate):
    _temp = post.dict()
    _temp['redirect'] = _temp.get("redirect") or _temp.get('component')
    _temp['component'] = _temp.get("component") or _temp.get('redirect') or "LAYOUT"
    menu = await Access.create(**_temp)
    await OperationLog.add_log(req, req.state.user.id, OpObject.role, OpMethod.create_object,
                               f"创建菜单(ID={menu.pk})")
    return SuccessResp(data="创建成功!")

