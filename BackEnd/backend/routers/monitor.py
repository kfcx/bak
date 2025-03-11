# -*- coding: utf-8 -*-
# @Time    : 2023/3/12
# @Author  : Naihe
# @File    : monitor.py
# @Software: PyCharm
from fastapi import APIRouter, Depends, Security

from ..dependencies import (check_permissions, PageSizePaginator)
from ..models.base import OperationLog
from ..schemas import OperationLogFilter, OperationLogItem, PageResp, SuccessResp
from ..utils.system import system

router = APIRouter(prefix='/system', tags=['系统管理'])


@router.get("/operation/logs", summary="查看日志", response_model=PageResp[OperationLogItem],
            dependencies=[Security(check_permissions, scopes=["Logs"])])
async def get_operation_logs(pg: PageSizePaginator = Depends(PageSizePaginator()),
                             filters: OperationLogFilter = Depends(OperationLogFilter)):
    logs_qs = OperationLog.all()
    page_data = await pg.output(logs_qs, filters.dict(exclude_none=True))
    return PageResp[OperationLogItem](data=page_data)


@router.get("/monitor", dependencies=[Security(check_permissions, scopes=["Monitor"])])
async def monitor():
    qs = system().GetSystemAllInfo()
    return SuccessResp(data=qs)

