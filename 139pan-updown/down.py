# -*- coding: utf-8 -*-
# @Time    : 2022/11/13
# @Author  : Naihe
# @File    : down.py
# @Software: PyCharm
import hashlib
import os
import time
from pathlib import Path
from urllib.request import urlopen
import math

from requests_toolbelt import MultipartEncoder
from tqdm import tqdm
import requests

from 断点续传 import distran

header = {
    "user-agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
}


# 进度条模块
def progressbar(url, path):
    start = time.time()  # 下载开始时间
    response = requests.get(url, stream=True)  # stream=True必须写上
    size = 0  # 初始化已下载大小
    chunk_size = 1024  # 每次下载的数据大小
    content_size = int(response.headers['content-length'])  # 下载文件总大小
    if path.is_file():
        if content_size >= path.stat().st_size:
            return
    try:
        if response.status_code == 200:  # 判断是否响应成功
            print('Start download,[File size]:{size:.2f} MB'.format(
                size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
            with open(path, 'wb') as file:  # 显示进度条
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    print('\r' + '[下载进度]:%s%.2f%%' % (
                    '>' * int(size * 50 / content_size), float(size / content_size * 100)), end=' ')
        end = time.time()  # 下载结束时间
        print('Download completed!,times: %.2f秒' % (end - start))  # 输出下载用时时间
    except:
        raise Exception("Error!")


def download_from_url(url, dst):
    file_size = int(urlopen(url).info().get('Content-Length', -1))
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:
        return file_size
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
    pbar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc=url.split('/')[-1])
    req = requests.get(url, headers=header, stream=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size


def download_link_path(url, path, chunk_size=512):
    r = requests.get(url=url, headers=header, stream=True)
    with open(path, 'wb') as f:
        # chunk是指定每次写入的大小，单位字节
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)


def download_from_url2(url, dst):
    '''
    :param url:  下载地址
    :param dst:  文件名称
    :return:
    '''
    #发起网络请求
    response = requests.get(url, stream=True)
    #获取返回的文件的大小
    file_size = int(response.headers['content-length'])
    #判断当前目录中是否有该文件，如果有获取文件的大小，从而实现断点续传
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    #如果文件大小已经超过了服务器返回的文件的大小，返回文件长度
    if first_byte >= file_size: #(4)
        return file_size
    #设置断点续传的位置
    header = {"Range": f"bytes=%s-%s"%(first_byte,file_size)}
    # desc :进度条的前缀
    # unit 定义每个迭代的单元。默认为"it"，即每个迭代，在下载或解压时，设为"B"，代表每个“块”。
    # unit_scale 默认为False，如果设置为1或者True，会自动根据国际单位制进行转换 (kilo, mega, etc.) 。比如，在下载进度条的例子中，如果为False，数据大小是按照字节显示，设为True之后转换为Kb、Mb。
    #total：总的迭代次数，不设置则只显示统计信息，没有图形化的进度条。设置为len(iterable)，会显示黑色方块的图形化进度条。
    pbar = tqdm(total=file_size, initial=first_byte,unit='B', unit_scale=True, desc=dst)
    #发送网络请求
    req = requests.get(url, headers=header, stream=True) #(5)
    #这里的二进制需要采用追加的方式写入文件，不然无法实现断点续传
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024): #(6)
            if chunk:
                #用于方便观察进度条，在下载大视频的时候去掉也能观察出来
                time.sleep(0.01)
                f.write(chunk)
                f.flush()
                pbar.update(1024)


def upload_slice_file(url, file_path):
    chunk_size = 1024*1024*2
    filename = file_path.split("\\")[-1:][0]
    total_size = os.path.getsize(file_path)
    current_chunk = 1
    total_chunk = math.ceil(total_size / chunk_size)

    while current_chunk <= total_chunk:
        start = (current_chunk - 1)*chunk_size
        end = min(total_size, start+chunk_size)
        with open(file_path, 'rb') as f:
            f.seek(start)
            file_chunk_data = f.read(end-start)
        data = MultipartEncoder(
            fields={
                "filename": filename,
                "totalSize": str(total_size),
                "currentChunk": str(current_chunk),
                "totalChunk": str(total_chunk),
                "md5": hashlib.md5(file_chunk_data).hexdigest(),
                "file": (filename, file_chunk_data, 'application/octet-stream')
            }
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Content-Type": data.content_type
        }
        with requests.post(url, headers=headers, data=data) as response:
            assert response.status_code == 200

        current_chunk = current_chunk + 1


def main():
    slice_size = 1024 * 1024

    Root = Path(r"Downloads")
    filename = ".exe"
    length = round((Root / filename).stat().st_size)
    py = distran()
    x_ = py.calc_divisional_range(length, length // slice_size)
    for i, v in enumerate(x_):
        s, e = v
        with open(Root/filename, "rb") as f:
            f.seek(s)
            data = f.read(e - s + 1)
            print(len(data))
        with open(filename, "ab+") as f:
            f.write(data)
            f.flush()



if __name__ == '__main__':
    main()
