# -*- coding: utf-8 -*-
import hashlib
import time
import re
import uuid
import json
import threading
import requests
from loguru import logger
from functools import lru_cache
from base64 import b64decode, b64encode
from urllib.parse import urljoin, unquote
from concurrent.futures import ThreadPoolExecutor


requests.packages.urllib3.disable_warnings()
# 忽略 https 警告
lock = threading.Lock()


def request_get(url, headers, retries=3, delay=2):
    for attempt in range(retries):
        try:
            with requests.get(url=url, headers=headers) as resp:
                content = resp.content
                return content
        except Exception as e:
            logger.warning(f"Get出错 {url} 报错内容 {e}, retrying in {delay} seconds...")
            time.sleep(delay)


class DLWorker:
    def __init__(self, name: str, url: str, range_start, range_end, cache_dir, finish_callback, user_agent):
        self.name = name
        self.url = url
        self.cache_filename = os.path.join(cache_dir, name + ".tmp")
        self.range_start = range_start  # 固定不动
        self.range_end = range_end  # 固定不动
        self.range_curser = range_start  # curser 所指尚未开始
        self.finish_callback = finish_callback  # 通知调用 DLWorker 的地方
        self.terminate_flag = False  # 该标志用于终结自己
        self.FINISH_TYPE = ""  # DONE 完成工作, HELP 需要帮忙, RETIRE 不干了
        self.user_agent = user_agent

    def __run(self):
        chunk_size = 10 * 1024 * 1024  # 10 MB
        # headers = {
        #     'User-Agent': self.user_agent,
        #     'Range': f'Bytes={self.range_curser}-{self.range_end}',
        #     'Accept-Encoding': '*'
        # }
        headers = {
            # "Host": url.split("/")[2],
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Accept": "*/*",
            "Accept-Encoding": "*",
            "Content-Type": "application/octet-stream",
            "Range": f"bytes={self.range_curser}-{self.range_end}",
        }
        try:
            with requests.get(self.url, stream=True, verify=False, headers=headers) as req:
                if 200 <= req.status_code <= 299:
                    with open(self.cache_filename, "wb") as cache:
                        for chunk in req.iter_content(chunk_size=chunk_size):
                            if self.terminate_flag:
                                break
                            cache.write(chunk)
                            self.range_curser += len(chunk)
                if not self.terminate_flag:  # 只有正常退出才能标记 DONE，但是三条途径都经过此处
                    self.FINISH_TYPE = "DONE"
        except requests.exceptions.ChunkedEncodingError as e:
            logger.error(f"下载分块出错：{e}")
            logger.debug("开始重试")
            self.retire()  # 放弃任务，开始重试
        self.finish_callback(self)  # 执行回调函数，根据 FINISH_TYPE 结局不同

    def start(self):
        threading.Thread(target=self.__run).start()  # 不能设置成守护线程

    def help(self):
        self.FINISH_TYPE = "HELP"
        self.terminate_flag = True

    def retire(self):
        self.FINISH_TYPE = "RETIRE"
        self.terminate_flag = True

    def __lt__(self, another):
        """用于排序"""
        return self.range_start < another.range_start

    def get_progress(self):
        """获得进度"""
        _progress = {
            "curser": self.range_curser,
            "start": self.range_start,
            "end": self.range_end
        }
        return _progress


class D2wnloader:
    def __init__(self, url: str, filename=None, download_dir: str = f".{os.sep}music{os.sep}", blocks_num: int = 8):
        assert 0 <= blocks_num <= 32
        self.url = url
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0'
        filename = filename or self.url.split("/")[-1].split("?")[0] or "temp.mp4"
        filename = parse.unquote(filename)
        self.filename = filename
        self.download_dir = download_dir
        self.blocks_num = blocks_num
        self.__bad_url_flag = False
        self.file_size = self.__get_size()
        if not self.__bad_url_flag:
            # 建立下载目录
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
            # 建立缓存目录
            self.cache_dir = f".{os.sep}music{os.sep}.cache{os.sep}"
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
            # 分块下载
            self.startdlsince = time.time()
            self.workers = []  # 装载 DLWorker
            self.AAEK = self.__get_AAEK_from_cache()  # 需要确定 self.file_size 和 self.block_num
            # 测速
            self.__done = threading.Event()
            self.__download_record = []
            threading.Thread(target=self.__supervise).start()  # 进度条
            # 主进程信号，直到下载结束后解除
            self.__main_thread_done = threading.Event()

    def __get_size(self):
        try:
            headers = {'User-Agent': self.user_agent}
            with requests.head(self.url, headers=headers) as req:
                content_length = req.headers["Content-Length"]
            return int(content_length)
            # with requests.get(self.url, headers=headers, stream=True) as req:
            #     content_length = req.headers["Content-Length"]
            # return int(content_length)
        except Exception as err:
            self.__bad_url_flag = True
            self.__whistleblower(f"[Error] {err}")
            return 0

    def __get_readable_size(self, size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        K = 1024.0
        while size >= K:
            size = size / K
            unit_index += 1
        return "%.1f %s" % (size, units[unit_index])

    def __get_cache_filenames(self):
        return glob.glob(f"{self.cache_dir}{self.filename}.*.tmp")

    def __get_ranges_from_cache(self):
        # 形如 ./cache/filename.1120.tmp
        ranges = []
        for filename in self.__get_cache_filenames():
            size = os.path.getsize(filename)
            if size > 0:
                cache_start = int(filename.split(".")[-2])
                cache_end = cache_start + size - 1
                ranges.append((cache_start, cache_end))
        ranges.sort(key=lambda x: x[0])  # 排序
        return ranges

    def __get_AAEK_from_cache(self):
        ranges = self.__get_ranges_from_cache()  # 缓存文件里的数据
        AAEK = []  # 根据 ranges 和 self.file_size 生成 AAEK | 未下载字节范围
        if len(ranges) == 0:
            AAEK.append((0, self.file_size - 1))
        else:
            for i, (start, end) in enumerate(ranges):
                if i == 0:
                    if start > 0:
                        AAEK.append((0, start - 1))
                next_start = self.file_size if i == len(ranges) - 1 else ranges[i + 1][0]
                if end < next_start - 1:
                    AAEK.append((end + 1, next_start - 1))
        return AAEK

    def __increase_ranges_slice(self, ranges: list, minimum_size=1024 * 1024):
        """增加分块数目，小于 minimum_size 就不再分割了"""
        assert len(ranges) > 0
        block_size = [end - start + 1 for start, end in ranges]
        index_of_max = block_size.index(max(block_size))
        start, end = ranges[index_of_max]
        halfsize = block_size[index_of_max] // 2
        if halfsize >= minimum_size:
            new_ranges = [x for i, x in enumerate(ranges) if i != index_of_max]
            new_ranges.append((start, start + halfsize))
            new_ranges.append((start + halfsize + 1, end))
        else:
            new_ranges = ranges
        return new_ranges

    def __ask_for_work(self, worker_num: int):
        """申请工作，返回 [work_range]，从 self.AAEK 中扣除。没工作的话返回 []。"""
        assert worker_num > 0
        task = []
        aaek_num = len(self.AAEK)
        if aaek_num == 0:  # 没任务了
            # TODO 这里挑 size 大的 DLWorker 调用 help
            self.__share_the_burdern()
            return []
        if aaek_num >= worker_num:  # 数量充足，直接拿就行了
            for _ in range(worker_num):
                task.append(self.AAEK.pop(0))
        else:  # 数量不足，需要切割
            slice_num = worker_num - aaek_num  # 需要分割几次
            task = self.AAEK  # 这个时候 task 就不可能是 [] 了
            self.AAEK = []
            for _ in range(slice_num):
                task = self.__increase_ranges_slice(task)
        task.sort(key=lambda x: x[0])
        return task

    def __share_the_burdern(self, minimum_size=1024 * 1024):
        """找出工作最繁重的 worker，调用他的 help。回调函数中会将他的任务一分为二。"""
        max_size = 0
        max_size_name = ""
        for w in self.workers:
            p = w.get_progress()
            size = p["end"] - p["curser"] + 1
            if size > max_size:
                max_size = size
                max_size_name = w.name
        if max_size >= minimum_size:
            for w in self.workers:
                if w.name == max_size_name:
                    w.help()
                    break

    def __give_back_work(self, worker: DLWorker):
        """接纳没干完的工作。需要按 size 从小到大排序。"""
        progress = worker.get_progress()
        curser = progress["curser"]
        end = progress["end"]
        if curser <= end:  # 校验一下是否是合理值
            self.AAEK.append((curser, end))
            self.AAEK.sort(key=lambda x: x[0])

    def __give_me_a_worker(self, start, end):
        worker = DLWorker(name=f"{self.filename}.{start}",
                          url=self.url, range_start=start, range_end=end, cache_dir=self.cache_dir,
                          finish_callback=self.__on_dlworker_finish,
                          user_agent=self.user_agent)
        return worker

    def __whip(self, worker: DLWorker):
        """鞭笞新来的 worker，让他去工作"""
        self.workers.append(worker)
        self.workers.sort()
        worker.start()

    def __on_dlworker_finish(self, worker: DLWorker):
        assert worker.FINISH_TYPE != ""
        self.workers.remove(worker)
        if worker.FINISH_TYPE == "HELP":  # 外包
            self.__give_back_work(worker)
            self.workaholic(2)
        elif worker.FINISH_TYPE == "DONE":  # 完工
            # 再打一份工，也可能打不到
            self.workaholic(1)
        elif worker.FINISH_TYPE == "RETIRE":  # 撂挑子
            # 把工作添加回 AAEK，离职不管了。
            self.__give_back_work(worker)
        # 下载齐全，开始组装
        if self.workers == [] and self.__get_AAEK_from_cache() == []:
            self.__sew()

    def start(self):
        # TODO 尝试整理缓存文件夹内的相关文件
        if not self.__bad_url_flag:
            # 召集 worker
            for start, end in self.__ask_for_work(self.blocks_num):
                worker = self.__give_me_a_worker(start, end)
                self.__whip(worker)
            # 卡住主进程
            self.__main_thread_done.wait()

    def stop(self):
        for w in self.workers:
            w.retire()
        while len(self.workers) != 0:
            time.sleep(0.5)
        self.AAEK = self.__get_AAEK_from_cache()

    def workaholic(self, n=1):
        """九九六工作狂。如果能申请到，就地解析；申请不到，__give_me_a_worker 会尝试将一个 worker 的工作一分为二；"""
        for s, e in self.__ask_for_work(n):
            worker = self.__give_me_a_worker(s, e)
            self.__whip(worker)

    def restart(self):
        self.stop()
        # 再次召集 worker。不调用 start 的原因是希望他继续卡住主线程。
        for start, end in self.__ask_for_work(self.blocks_num):
            worker = self.__give_me_a_worker(start, end)
            self.__whip(worker)

    def __supervise(self):
        """万恶的督导：监视下载速度、进程数；提出整改意见；"""
        REFRESH_INTERVAL = 1  # 每多久输出一次监视状态
        LAG_COUNT = 10  # 计算过去多少次测量的平均速度
        WAIT_TIMES_BEFORE_RESTART = 30  # 乘以时间就是等待多久执行一次 restart
        SPEED_DEGRADATION_PERCENTAGE = 0.5  # 速度下降百分比
        self.__download_record = []
        maxspeed = 0
        wait_times = WAIT_TIMES_BEFORE_RESTART
        while not self.__done.is_set():
            dwn_size = sum([os.path.getsize(cachefile) for cachefile in self.__get_cache_filenames()])
            self.__download_record.append({"timestamp": time.time(), "size": dwn_size})
            if len(self.__download_record) > LAG_COUNT:
                self.__download_record.pop(0)
            s = self.__download_record[-1]["size"] - self.__download_record[0]["size"]
            t = self.__download_record[-1]["timestamp"] - self.__download_record[0]["timestamp"]
            if not t == 0:
                speed = s / t
                readable_speed = self.__get_readable_size(speed)  # 变成方便阅读的样式
                percentage = self.__download_record[-1]["size"] / self.file_size * 100
                status_msg = f"\r[info] {percentage:.1f} % | {readable_speed}/s | {len(self.workers)}+{threading.active_count() - len(self.workers)} {(time.time() - self.startdlsince):.0f}s"
                self.__whistleblower(status_msg)
                # 监测下载速度下降
                maxspeed = max(maxspeed, speed)
                EPSILON = 1e-5  # 表示很小的值，避免除以零
                # 构建几个表达式用于简化逻辑，首先是前提条件
                time_over = wait_times < 0  # 容忍时间到了
                not_finished = not self.__done.is_set()  # 尚未完成下载
                # 情况 1. 速度在 1MB/s 以下，并且下降明显（如果速度在 1MB/s 以上可以先不管）
                speed_drops_significantly = (maxspeed - speed + EPSILON) / (
                        maxspeed + EPSILON) > SPEED_DEGRADATION_PERCENTAGE
                speed_under_threshold = speed < 1024 * 1024  # 1MB
                scene_1 = speed_drops_significantly and speed_under_threshold
                # 情况 2. 速度很慢
                scene_2 = speed < 16 * 1024  # 16KB
                if time_over and not_finished and (scene_1 or scene_2):
                    self.__whistleblower("\r[info] speed degradation, restarting...")  # 有问题 err
                    self.restart()
                    maxspeed = 0
                    wait_times = WAIT_TIMES_BEFORE_RESTART
                else:
                    wait_times -= 1
            time.sleep(REFRESH_INTERVAL)

    def __sew(self):
        self.__done.set()
        chunk_size = 10 * 1024 * 1024
        with open(f"{os.path.join(self.download_dir, self.filename)}", "wb") as f:
            for start, _ in self.__get_ranges_from_cache():
                cache_filename = f"{self.cache_dir}{self.filename}.{start}.tmp"
                with open(cache_filename, "rb") as cache_file:
                    data = cache_file.read(chunk_size)
                    while data:
                        f.write(data)
                        f.flush()
                        data = cache_file.read(chunk_size)
        self.clear()
        self.__whistleblower("\r")
        self.__main_thread_done.set()

    def __whistleblower(self, saying: str):
        # iPhone 12 mini 每行显示45个字符，等款字体
        # 这里假设 \r 如果出现一定位于字符串的起始
        wordsCountOfEachLine = 45
        if len(saying.replace("\r", "")) > wordsCountOfEachLine:
            sys.stdout.write(saying[:wordsCountOfEachLine])
        else:
            sys.stdout.write(saying + " " * (wordsCountOfEachLine - len(saying.replace("\r", ""))))

    def clear(self):
        for filename in self.__get_cache_filenames():
            os.remove(filename)



def main():
    # 使用第三方接口获取音频
    netease = Netease()

    chanty = Chanty()
    max_workers = 4  # 线程下载上传
    part_size = 12
    total_size = len(playlist)
    counter = (total_size // part_size) + 1
    for i in range(counter):
        if counter > 0:
            for _ in range(30):
                if (time.time() - int(netease.r.get("163lock") or 0)) > 30:  # 检测是否上锁
                    break
                time.sleep(1)
            netease.r.set("163lock", int(time.time()))  # 上锁
            if i != (counter - 1):
                ids = playids[part_size * i:part_size * (i + 1)]
            else:
                logger.info("已上传完大半")
                ids = playids[-(total_size % part_size):]
            [ids.remove(iid) for iid in netease.r.hkeys("new_netease") if iid in ids]  # 去除已下载
            task = netease.r.hgetall("163task")
            [ids.remove(k) for k, v in task.items() if
             k in ids and json.loads(v)["u"] != user and (int(time.time()) - int(json.loads(v)["t"])) < 3600]
            if len(ids) == 0:
                netease.r.set("163lock", "0")  # 解锁
                continue
            t = int(time.time())
            netease.r.hmset("163task", {i: json.dumps({"u": user, "t": t}) for i in ids})  # 任务上锁
            netease.r.set("163lock", "0")  # 解锁

            url_data = netease.get_url(ids)  # 批量获取链接
            logger.info("正在批量获取音乐链接")
            data = {str(i["rid"]): i if i["code"] == 200 else ids.remove(str(i["rid"])) for i in url_data if i["url"]}    # 保留有记录信息
            if not data:
                print("not data")
                continue
            if len(ids) != len(data):
                logger.error(f"部分歌曲id未获取到链接! {len(data)}")
                with open("temp2", "a") as f:
                    f.write(f'{",".join(ids)} \n')

            logger.info("开始进行转存")
            while True:
                parts = {}  # 记录上传成功记录
                # 构成参数
                urls = [[i["url"], str(i["rid"]), json.loads(playlist[str(i["rid"])])["name"] +
                         os.path.splitext(os.path.basename(i['url']).split("?")[0])[1]]
                        for i in data.values() if type(i) == dict]
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(netease.task2, v[2], {
                        "id": v[1],
                        "url": v[0],  # 转存链接
                        "br": "0",
                        "size": str(int(float(data[v[1]]["size"])*1024*1024)),
                        "md5": "0",
                        "level": data[v[1]]["quality"],
                        "type": "0",
                        "time": "0",
                        "musicId": "0",
                    }, chanty): v for v in urls}
                    for future in futures:
                        iid, url = future.result()
                        if url:
                            parts.update({iid: True})
                        else:
                            logger.warning(f"{iid} 上传失败")

                    if len(parts) != len(urls):  # 不能用data比较，存在偏差
                        [data.pop(iid, None) for iid in parts.keys()]  # 去除已下载
                        logger.warning("下载音乐部分缺失!")
                        time.sleep(3)
                        continue
                    else:
                        break

    logger.success("任务完成")


if __name__ == '__main__':
    main()

