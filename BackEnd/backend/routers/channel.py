# -*- coding: utf-8 -*-
# @Time    : 2023/3/2
# @Author  : Naihe
# @File    : channel.py
# @Software: PyCharm
from typing import Union
from aioredis import Redis
from fastapi import APIRouter, Depends, Path, Request, Security
from tortoise.exceptions import OperationalError
from tortoise.transactions import in_transaction

from ..dependencies import check_permissions, get_redis, PageSizePaginator, get_current_active_user
from ..enums import OperationMethod as OpMethod, OperationObject as OpObject
from ..models import OperationLog, Channel, Role, User
from ..schemas import (ChannelCreate, ChannelFilter, ChannelInfo, ChannelUpdate, FailResp, PageResp, SingleResp,
                       SuccessResp)
from ..utils.tools import hash_url

router = APIRouter(prefix='/channel', tags=['频道管理'])


# @router.get('/hot', response_model=Union[PageResp[ChannelInfo], FailResp], summary='热门频道')
# async def get_hot_channel(pg: PageSizePaginator = Depends(PageSizePaginator()),
#                             redis: Redis = Depends(get_redis)):
#     # 获取热门频道
#     hot_channel = await redis.zrevrange('hot_channel', 0, 10, withscores=True)
#     # 获取频道信息
#     channel_ids = [int(i[0]) for i in hot_channel]
#     channel_info = await Channel.filter(id__in=channel_ids).all()
#     # 组装数据
#     data = []
#     for i in channel_info:
#         data.append({
#             'id': i.id,
#             'hash_id': i.hash_id,
#             'tvg_id': i.tvg_id,
#             'tvg_country': i.tvg_country,
#             'tvg_language': i.tvg_language,
#             'tvg_logo': i.tvg_logo,
#             'group_title': i.group_title,
#             'title': i.title,
#             'url': i.url,
#             'description': i.description,
#             'status': i.status,
#             'hot': hot_channel[channel_ids.index(i.id)][1],
#         })
#     return PageResp[ChannelInfo](data=data)


@router.get('/hot', response_model=Union[SuccessResp, FailResp], summary='热门频道')
async def get_hot_channel():
    data = [{
  'id': '11',
  'hash_id': '521926ac4da23b9b',
  'title': 'CCTV1',
  'group_title': '儿童与青少年',
  'tvg_country': '中国',
  'tvg_language': '中文',
  'description': '达芬奇频道是一个以文化、艺术、教育、科技等内容为主的频道，涵盖了电视剧、电影、纪录片、综艺、音乐等多种类型的节目。该频道以传播文化、弘扬正能量为宗旨，致力于打造高品质的电视节目，让观众在欣赏节目的同时，感受到文化的魅力和人文的温度。除了电视播出外，达芬奇频道也提供了网络直播和点播服务，用户可以通过官方网站或者手机客户端观看相关节目。在现今快节奏的生活中，达芬奇频道为观众提供了一个放松心情、开阔眼界的平台，是广大观众了解文化、追求精神满足的重要途径之一。',
  'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV1.png',
  'url': 'http://cctvwbndali.v.myalicdn.com/cctvwbnd/cctv1_2/index.m3u8',
},
            {
      'id': '12',
      'hash_id': '2e48ec11263347cd',
      'title': 'CCTV2',
      'group_title': '综合',
      'tvg_country': '中国',
      'tvg_language': '中文',
      'description': "爱尔达娱乐台是一个面向全球华人的娱乐频道，旗下拥有多档热门综艺节目。该频道以提供优质的娱乐节目为主要目标，包括音乐、影视、综艺、时尚等元素，涵盖了众多年龄层和兴趣爱好的观众。爱尔达娱乐台在制作节目时注重创新和多样性，提供了多种形式的节目，如选秀、真人秀、访谈、演唱会等，满足了观众不同的需求。此外，爱尔达娱乐台还通过互联网和移动端提供了直播和点播服务，让观众可以随时随地收看喜欢的节目。总之，爱尔达娱乐台是一个充满活力和创意的娱乐频道，为观众提供了丰富多彩的节目内容，成为了广大华人喜爱的娱乐平台之一。",
      'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV2.png',
      'url': 'http://cctvwbndali.v.myalicdn.com/cctvwbnd/cctv2_2/index.m3u8',
    },
            {
      'id': '13',
      'hash_id': '9b51c56ece63f660',
      'title': 'CCTV3',
      'group_title': '综合',
      'tvg_country': '中国',
      'tvg_language': '中文',
      'description': "靖天综合台是一家面向全球中文观众的综合性电视频道，旨在为广大中文观众提供最新、最全面的新闻、娱乐、文化、教育等多方面的内容。该频道涵盖了众多类型的节目，包括新闻、财经、综艺、文化、时尚等多个方面的内容，致力于打造高品质的电视娱乐节目。",
      'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV3.png',
      'url': 'http://39.134.66.110/PLTV/88888888/224/3221225799/index.m3u8',
    },
            {
      'id': '14',
      'hash_id': '4c324721340382b9',
      'title': 'CCTV5+',
      'group_title': '音乐综艺',
      'tvg_country': '中国',
      'tvg_language': '中文',
      'description': "TVBS欢乐台是台湾的一个综艺娱乐频道，属于TVBS媒体集团旗下的电视频道之一。该频道以提供高质量的综艺节目为主要目标，包括选秀、真人秀、访谈、游戏等元素，涵盖了众多年龄层和兴趣爱好的观众。TVBS欢乐台通过不断创新和突破，在制作节目时注重多样性和趣味性，吸引了大量观众的关注。此外，TVBS欢乐台还通过互联网和移动端提供了直播和点播服务，让观众可以随时随地收看喜欢的节目。总之，TVBS欢乐台是一个充满活力和创意的综艺频道，为观众提供了丰富多彩的节目内容，成为了台湾地区广大观众喜爱的娱乐平台之一。",
      'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV5+.png',
      'url': 'http://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221225761/index.m3u8',
    },
            {
      'id': '15',
      'hash_id': '964603076bce4fe5',
      'title': 'CCTV6',
      'group_title': '音乐综艺',
      'tvg_country': '中国',
      'tvg_language': '中文',
      'description': "韩国娱乐台是一家专注于韩国娱乐圈的电视频道，旨在向全球观众介绍韩国的娱乐文化和艺术，涵盖了韩流音乐、电视剧、电影、综艺节目等多个方面的内容。该频道的节目风格轻松、欢乐，涵盖了众多年龄层和兴趣爱好的观众。",
      'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV6.png',
      'url': 'http://dbiptv.sn.chinamobile.com/PLTV/88888893/224/3221226393/index.m3u8',
    }]
    data.reverse()
    return SuccessResp(data=data)


@router.get('/recommend', response_model=Union[SuccessResp, FailResp], summary='猜你喜欢')
async def get_recommend_channel():
    data = [{
        'id': '11',
        'hash_id': '521926ac4da23b9b',
        'title': 'CCTV1',
        'group_title': '儿童与青少年',
        'tvg_country': '中国',
        'tvg_language': '中文',
        'description': '达芬奇频道是一个以文化、艺术、教育、科技等内容为主的频道，涵盖了电视剧、电影、纪录片、综艺、音乐等多种类型的节目。该频道以传播文化、弘扬正能量为宗旨，致力于打造高品质的电视节目，让观众在欣赏节目的同时，感受到文化的魅力和人文的温度。除了电视播出外，达芬奇频道也提供了网络直播和点播服务，用户可以通过官方网站或者手机客户端观看相关节目。在现今快节奏的生活中，达芬奇频道为观众提供了一个放松心情、开阔眼界的平台，是广大观众了解文化、追求精神满足的重要途径之一。',
        'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV1.png',
        'url': 'http://cctvwbndali.v.myalicdn.com/cctvwbnd/cctv1_2/index.m3u8',
    },
        {
            'id': '12',
            'hash_id': '2e48ec11263347cd',
            'title': 'CCTV2',
            'group_title': '综合',
            'tvg_country': '中国',
            'tvg_language': '中文',
            'description': "爱尔达娱乐台是一个面向全球华人的娱乐频道，旗下拥有多档热门综艺节目。该频道以提供优质的娱乐节目为主要目标，包括音乐、影视、综艺、时尚等元素，涵盖了众多年龄层和兴趣爱好的观众。爱尔达娱乐台在制作节目时注重创新和多样性，提供了多种形式的节目，如选秀、真人秀、访谈、演唱会等，满足了观众不同的需求。此外，爱尔达娱乐台还通过互联网和移动端提供了直播和点播服务，让观众可以随时随地收看喜欢的节目。总之，爱尔达娱乐台是一个充满活力和创意的娱乐频道，为观众提供了丰富多彩的节目内容，成为了广大华人喜爱的娱乐平台之一。",
            'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV2.png',
            'url': 'http://cctvwbndali.v.myalicdn.com/cctvwbnd/cctv2_2/index.m3u8',
        },
        {
            'id': '13',
            'hash_id': '9b51c56ece63f660',
            'title': 'CCTV3',
            'group_title': '综合',
            'tvg_country': '中国',
            'tvg_language': '中文',
            'description': "靖天综合台是一家面向全球中文观众的综合性电视频道，旨在为广大中文观众提供最新、最全面的新闻、娱乐、文化、教育等多方面的内容。该频道涵盖了众多类型的节目，包括新闻、财经、综艺、文化、时尚等多个方面的内容，致力于打造高品质的电视娱乐节目。",
            'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV3.png',
            'url': 'http://39.134.66.110/PLTV/88888888/224/3221225799/index.m3u8',
        },
        {
            'id': '14',
            'hash_id': '4c324721340382b9',
            'title': 'CCTV5+',
            'group_title': '音乐综艺',
            'tvg_country': '中国',
            'tvg_language': '中文',
            'description': "TVBS欢乐台是台湾的一个综艺娱乐频道，属于TVBS媒体集团旗下的电视频道之一。该频道以提供高质量的综艺节目为主要目标，包括选秀、真人秀、访谈、游戏等元素，涵盖了众多年龄层和兴趣爱好的观众。TVBS欢乐台通过不断创新和突破，在制作节目时注重多样性和趣味性，吸引了大量观众的关注。此外，TVBS欢乐台还通过互联网和移动端提供了直播和点播服务，让观众可以随时随地收看喜欢的节目。总之，TVBS欢乐台是一个充满活力和创意的综艺频道，为观众提供了丰富多彩的节目内容，成为了台湾地区广大观众喜爱的娱乐平台之一。",
            'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV5+.png',
            'url': 'http://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221225761/index.m3u8',
        },
        {
            'id': '15',
            'hash_id': '964603076bce4fe5',
            'title': 'CCTV6',
            'group_title': '音乐综艺',
            'tvg_country': '中国',
            'tvg_language': '中文',
            'description': "韩国娱乐台是一家专注于韩国娱乐圈的电视频道，旨在向全球观众介绍韩国的娱乐文化和艺术，涵盖了韩流音乐、电视剧、电影、综艺节目等多个方面的内容。该频道的节目风格轻松、欢乐，涵盖了众多年龄层和兴趣爱好的观众。",
            'tvg_logo': 'http://epg.51zmt.top:8000/tb1/CCTV/CCTV6.png',
            'url': 'http://dbiptv.sn.chinamobile.com/PLTV/88888893/224/3221226393/index.m3u8',
        }]
    data.reverse()
    return SuccessResp(data=data)


@router.get('', summary='频道列表', response_model=PageResp[ChannelInfo],
            dependencies=[Security(check_permissions, scopes=["channel_retrieve"])])
async def get_all_channel(me: User = Depends(get_current_active_user),
                          pg: PageSizePaginator = Depends(PageSizePaginator()),
                          filters: ChannelFilter = Depends(ChannelFilter)):
    if me.is_superuser:
        channel_qs = Channel.all().prefetch_related('role')
    else:
        channel_qs = Channel.filter(role__user__id=me.pk).prefetch_related("role")

    page_data = await pg.output(channel_qs, filters.dict(exclude_defaults=True))
    return PageResp[ChannelInfo](data=page_data)


@router.post("", summary="添加频道", dependencies=[Security(check_permissions, scopes=["channel_create"])])
async def channel_add(req: Request, post: ChannelCreate):
    post.hash_id = hash_url(post.url)
    # 过滤频道
    get_channel = await Channel.get_or_none(hash_id=post.hash_id)
    if get_channel is not None:
        return FailResp(code=20201, msg=f"频道 {post.title} 已经存在!")

    try:
        async with in_transaction():
            # 创建频道
            create_channel = await Channel.create(**post.dict())
            await OperationLog.add_log(req, req.state.user.id, OpObject.account, OpMethod.create_object,
                                       f"创建频道(ID={create_channel.pk})")

            if post.roles:
                # 有分配权限
                roles = await Role.filter(id__in=post.roles, status=True)
                await create_channel.role.add(*roles)
                await OperationLog.add_log(req, req.state.user.id, OpObject.account, OpMethod.allocate_resources,
                                           f"分配权限(roleIDs={post.roles})")
            return SuccessResp(data=f"频道 {create_channel.title} 创建成功")
    except OperationalError:
        return FailResp(code=20503, msg="添加频道失败")


@router.get('/{channel_id}', response_model=Union[SingleResp[ChannelInfo], FailResp], summary='查看频道详情',
            dependencies=[Security(check_permissions, scopes=["channel_retrieve"])])
async def get_channel_by_id(me: User = Depends(get_current_active_user),
                            channel_id: int = Path(..., gt=0, description='频道ID')):
    if me.is_superuser:
        channel = await Channel.get_or_none(pk=channel_id)
    else:
        channel = await Channel.filter(role__user__id=me.pk).get_or_none(pk=channel_id)
    if channel is None:
        return FailResp(code=20201, msg='频道不存在')
    await channel.fetch_related('role')
    channel_info = ChannelInfo.from_orm(channel)
    return SingleResp[ChannelInfo](data=channel_info)


@router.put("/{cid}", summary="修改频道", dependencies=[Security(check_permissions, scopes=["channel_update"])])
async def channel_update(req: Request, post: ChannelUpdate, cid: int = Path(..., gt=0),
                         redis: Redis = Depends(get_redis)):
    channel = await Channel.get_or_none(pk=cid)
    # 不存在的频道
    if channel is None:
        return FailResp(code=20501, msg="频道不存在")
    hash_id = hash_url(post.url)
    if channel.hash_id != hash_id:  # hash值不同才添加
        check_channelname = await Channel.get_or_none(hash_id=hash_id)
        if check_channelname:
            return FailResp(code=20502, msg=f"用户名{channel.title}已存在")

    try:
        async with in_transaction():
            # 更新频道
            post.hash_id = hash_id  # 更新hash_id
            update_data = post.dict(exclude_unset=True, exclude_none=True)
            await channel.update_from_dict(update_data)
            await channel.save()
            # 清空角色
            await channel.role.clear()
            # 修改权限
            if post.roles:
                # 把缓存清掉 奇怪，为什么要删除redis内容，有缓存吗？
                await redis.delete(f"cache:perm_code:{channel.hash_id}", f"cache:router_tree:{channel.hash_id}")
                roles = await Role.filter(status=True, id__in=post.roles).all()
                # 分配角色
                await channel.role.add(*roles)
    except OperationalError:
        return FailResp(code=20503, msg="更新账号信息失败")
    # 记录你操作日志
    await OperationLog.add_log(req, req.state.user.id, OpObject.account, OpMethod.update_object,
                               f"修改频道(ID={cid})")
    # 开始返回信息
    await channel.fetch_related('role')

    data = ChannelInfo.from_orm(channel)
    return SingleResp[ChannelInfo](data=data)


@router.delete("/{cid}", summary="删除频道", dependencies=[Security(check_permissions, scopes=["channel_delete"])])
async def channel_del(req: Request, cid: int = Path(..., gt=0)):
    delete_action = await Channel.filter(pk=cid).delete()
    if not delete_action:
        return FailResp(code=20302, msg=f"频道{cid}删除失败!")
    await OperationLog.add_log(req, req.state.user.id, OpObject.account, OpMethod.delete_object,
                               f"删除频道(ID={cid})")
    return SuccessResp(data="删除成功")

