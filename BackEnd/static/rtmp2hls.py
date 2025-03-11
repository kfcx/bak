# -*- coding: utf-8 -*-
# @Time    : 2023/3/19
# @Author  : Naihe
# @File    : rtmp2hls.py
# @Software: PyCharm
import os
import asyncio
import logging
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.routing import Route

app = FastAPI()

streams = {}
timeouts = {}
logging.basicConfig(filename='app.log', level=logging.DEBUG)


async def check_timeout(stream_id):
    global streams
    global timeouts

    await asyncio.sleep(60)

    if stream_id in timeouts:
        timeouts[stream_id] += 1
    else:
        timeouts[stream_id] = 1

    if timeouts[stream_id] >= 5:
        if stream_id in streams:
            streams[stream_id].terminate()
            del streams[stream_id]
            del timeouts[stream_id]


async def start_stream(stream_id, rtmp_url, output_path, ffmpeg_options):
    global streams
    global timeouts

    if stream_id in streams:
        raise ValueError("Stream already exists")

    command = [
        "ffmpeg",
        "-i",
        rtmp_url,
        *ffmpeg_options,
        "-f",
        "hls",
        output_path
    ]

    streams[stream_id] = subprocess.Popen(command)
    timeouts[stream_id] = 0


@app.get("/start_stream")
async def start_stream_route(rtmp_url: str, stream_id: str, ffmpeg_options: str = ""):
    global streams

    if stream_id in streams:
        return {"detail": "Stream already started"}

    output_path = f"./hls_output/{stream_id}/"

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ffmpeg_options = ffmpeg_options.split()

    try:
        await start_stream(stream_id, rtmp_url, output_path, ffmpeg_options)
    except ValueError as e:
        logging.error(f"Error starting stream {stream_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    logging.info(f"Started stream {stream_id}")
    return {"detail": "Stream started"}


@app.get("/stop_stream")
async def stop_stream_route(stream_id: str):
    global streams
    global timeouts

    if stream_id not in streams:
        return {"detail": "Stream does not exist"}

    streams[stream_id].terminate()
    del streams[stream_id]
    del timeouts[stream_id]

    return {"detail": "Stream stopped"}


@app.get("/streams/{stream_id}/{file}")
async def get_hls_file(request: Request, background_tasks: BackgroundTasks, stream_id: str, file: str):
    global streams
    global timeouts

    if stream_id not in streams:
        raise HTTPException(status_code=404, detail="Stream does not exist")

    file_path = f"./hls_output/{stream_id}/{file}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    background_tasks.add_task(check_timeout, stream_id)

    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# python3 fastapi ffmpeg代理缓存rtmp转hls，当用户调用时开始转换，无人访问时停止转换
# 需要满足以下需求：
# 1、输入的RTMP流地址和输出的HLS流地址不一定是固定的，需要根据实际情况进行修改
# 2、转换时的FFmpeg参数也可能需要根据实际情况进行修改，例如视频分辨率、码率等。
# 3、定时任务的时间间隔可以根据实际情况进行修改，例如检查用户是否有访问的时间间隔和空闲时间间隔。
# 4、需要添加日志记录和错误处理，以便在出现错误时进行排查和修复。
# 5、需要支持多个RTMP流转换，使用多线程或异步任务来处理转换。
