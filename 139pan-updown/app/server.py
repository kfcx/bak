import re
import logging
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import aiofiles.os
from aiohttp import web
from aiohttp.web import middleware
from aiohttp.web_request import Request

from app.config import STATIC_ROOT, Root
from app.utile import write_file, unique_filename, callback, addUri
from app.upload import uploads

static_path = Path(__file__).parent.joinpath("static").absolute()

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.post("/offline")
async def get_offline(request: web.Request):
    data = (await request.post()).get("data")
    typed = (await request.post()).get("type")
    if data:
        datas = list(filter(None, data.split("\r\n")))
        for data in datas:
            _ = list(filter(None, data.split("@")))
            if len(_) != 1 and len(_) != 2:
                continue
            STATIC = STATIC_ROOT / (urlparse(_[0]).path.split("/").pop() or str(uuid4()))

            if typed.lower() != "aria2":
                await addUri(_.pop(), str(STATIC_ROOT), STATIC.name)
            else:
                file, hmd5, length = await callback(STATIC, _.pop())
                if length == 0:
                    import aiofiles.os
                    logger.error(f"File {file} 获取失败")
                    await aiofiles.os.remove(file)
                else:
                    await uploads(file, hmd5, length)
        return web.Response(text="ok")
    else:
        return web.Response(text="off")


@routes.get("/offline")
async def get_online(_):
    return web.FileResponse(static_path / "put.html")


@routes.post("/online")
async def post_online(request: web.Request):
    try:
        fields = await request.multipart()
    except (ValueError, AssertionError):
        raise web.HTTPBadRequest(
            text="multipart/form-data expected in request body",
        )

    files_received = 0  # 接收文件数量

    async for field in fields:
        if field.name != "file" or not Path(field.filename or "").name:
            continue
        filename = Path(field.filename or "").name
        logger.info("Receiving %s", filename)
        if not request.app["overwrite_duplicates"]:
            filename = await unique_filename(filename)

        hmd5, length = await write_file(field, filename)
        logger.info("Completed %s", filename)
        files_received += 1
        await uploads(STATIC_ROOT / filename, hmd5, length)
        await aiofiles.os.remove(STATIC_ROOT / filename)
        print("下载完成")
    if files_received:
        raise web.HTTPSeeOther(".")
    else:
        raise web.HTTPBadRequest(text="file field is required")


@routes.get("/online")
async def get_online(_):
    return web.FileResponse(static_path / "index.html")


@routes.get("/")
async def index(_):
    return web.Response(text="hello")


@middleware
async def middleware(request, handler):
    resp = await handler(request)
    return resp


routes.static("/", static_path)


def make_app(*, overwrite_duplicates=False):
    app = web.Application(middlewares=[middleware])
    app.add_routes(routes)
    app["overwrite_duplicates"] = overwrite_duplicates

    return app

