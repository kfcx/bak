import binascii
from hashlib import md5
import json
from loguru import logger
from base64 import b64decode, b64encode
import sys
import re
from typing import Any, Dict, List, Optional
import asyncio
import hashlib
from uuid import uuid4
import time
import httpx
import oss2

CLIENT_ID = "YNxT9w7GMdWvEOKa"
CLIENT_SECRET = "dbw2OtmVEeuUvIptb1Coyg"
CLIENT_VERSION = "1.47.1"
PACKAG_ENAME = "com.pikcloud.pikpak"
SDK_VERSION = "2.0.4.204000 "
APP_NAME = PACKAG_ENAME
SALTS = [
    "Gez0T9ijiI9WCeTsKSg3SMlx",
    "zQdbalsolyb1R/",
    "ftOjr52zt51JD68C3s",
    "yeOBMH0JkbQdEFNNwQ0RI9T3wU/v",
    "BRJrQZiTQ65WtMvwO",
    "je8fqxKPdQVJiy1DM6Bc9Nb1",
    "niV",
    "9hFCW2R1",
    "sHKHpe2i96",
    "p7c5E6AcXQ/IJUuAEC9W6",
    "",
    "aRv9hjc9P+Pbn+u3krN6",
    "BzStcgE8qVdqjEH16l4",
    "SqgeZvL5j9zoHP95xWHt",
    "zVof5yaJkPe3VFpadPof",
]


class PikpakException(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_timestamp() -> int:
    return int(time.time() * 1000)


def device_id_generator() -> str:
    return str(uuid4()).replace("-", "")


def captcha_sign(device_id: str, timestamp: str) -> str:
    """
    Generate a captcha sign.

    在网页端的js中, 搜索 captcha_sign, 可以找到对应的js代码

    """
    sign = CLIENT_ID + CLIENT_VERSION + PACKAG_ENAME + device_id + timestamp
    for salt in SALTS:
        sign = hashlib.md5((sign + salt).encode()).hexdigest()
    return f"1.{sign}"


def generate_device_sign(device_id, package_name):
    signature_base = f"{device_id}{package_name}1appkey"

    # 计算 SHA-1 哈希
    sha1_hash = hashlib.sha1()
    sha1_hash.update(signature_base.encode("utf-8"))
    sha1_result = sha1_hash.hexdigest()

    # 计算 MD5 哈希
    md5_hash = hashlib.md5()
    md5_hash.update(sha1_result.encode("utf-8"))
    md5_result = md5_hash.hexdigest()

    device_sign = f"div101.{device_id}{md5_result}"

    return device_sign


def build_custom_user_agent(device_id, user_id):
    device_sign = generate_device_sign(device_id, PACKAG_ENAME)

    user_agent_parts = [
        f"ANDROID-{APP_NAME}/{CLIENT_VERSION}",
        "protocolVersion/200",
        "accesstype/",
        f"clientid/{CLIENT_ID}",
        f"clientversion/{CLIENT_VERSION}",
        "action_type/",
        "networktype/WIFI",
        "sessionid/",
        f"deviceid/{device_id}",
        "providername/NONE",
        f"devicesign/{device_sign}",
        "refresh_token/",
        f"sdkversion/{SDK_VERSION}",
        f"datetime/{get_timestamp()}",
        f"usrno/{user_id}",
        f"appname/{APP_NAME}",
        "session_origin/",
        "grant_type/",
        "appid/",
        "clientip/",
        "devicename/Xiaomi_M2004j7ac",
        "osversion/13",
        "platformversion/10",
        "accessmode/",
        "devicemodel/M2004J7AC",
    ]

    return " ".join(user_agent_parts)


def calculate_sha1(filepath, chunk_size=10240):
    sha1 = hashlib.sha1()
    content = b""
    with open(filepath, "rb") as fp:
        while chunk := fp.read(chunk_size):
            sha1.update(chunk)
            content += chunk
    return sha1.hexdigest(), content


class PikPakApi:
    """
    Attributes:
        CLIENT_ID: str - PikPak API client id
        CLIENT_SECRET: str - PikPak API client secret
        PIKPAK_API_HOST: str - PikPak API host
        PIKPAK_USER_HOST: str - PikPak user API host

        username: str - username of the user
        password: str - password of the user
        encoded_token: str - encoded token of the user with access and refresh tokens
        access_token: str - access token of the user , expire in 7200
        refresh_token: str - refresh token of the user
        user_id: str - user id of the user
        httpx_client_args: dict - extra arguments for httpx.AsyncClient (https://www.python-httpx.org/api/#asyncclient)
    """

    PIKPAK_API_HOST = "api-drive.mypikpak.com"
    PIKPAK_USER_HOST = "user.mypikpak.com"

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None,
                 encoded_token: Optional[str] = None, httpx_client_args: Optional[Dict[str, Any]] = {},
                 device_id: Optional[str] = None):
        """
        username: str - username of the user
        password: str - password of the user
        encoded_token: str - encoded token of the user with access and refresh token
        httpx_client_args: dict - extra arguments for httpx.AsyncClient (https://www.python-httpx.org/api/#asyncclient)
        """

        self.username = username
        self.password = password
        self.encoded_token = encoded_token

        self.access_token = None
        self.refresh_token = None
        self.user_id = None

        # device_id is used to identify the device, if not provided, a random device_id will be generated, 32 characters
        self.device_id = (device_id if device_id else md5(f"{self.username}{self.password}".encode()).hexdigest())
        self.captcha_token = None

        self.httpx_client = httpx.AsyncClient(**httpx_client_args if httpx_client_args else {})

        self._path_id_cache: Dict[str, Any] = {}

        self.user_agent: Optional[str] = None

        if self.encoded_token:
            self.decode_token()
        elif self.username and self.password:
            pass
        else:
            raise PikpakException("username and password or encoded_token is required")

    def build_custom_user_agent(self) -> str:

        self.user_agent = build_custom_user_agent(
            device_id=self.device_id,
            user_id=self.user_id if self.user_id else "",
        )
        return self.user_agent

    def get_headers(self, access_token: Optional[str] = None) -> Dict[str, str]:
        """
        Returns the headers to use for the requests.
        """
        headers = {
            "User-Agent": (
                self.build_custom_user_agent()
                if self.captcha_token
                else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            "Content-Type": "application/json; charset=utf-8",
        }

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        if self.captcha_token:
            headers["X-Captcha-Token"] = self.captcha_token
        if self.device_id:
            headers["X-Device-id"] = self.device_id
        return headers

    async def _make_request(self, method: str, url: str, data=None, params=None, headers=None) -> Dict[str, Any]:
        backoff_seconds = 3
        error_decription = ""
        for i in range(3):  # retries
            # headers can be different for each request with captcha
            if headers is None:
                req_headers = self.get_headers()
            else:
                req_headers = headers
            try:
                response = await self.httpx_client.request(method, url, json=data, params=params, headers=req_headers, )
            except httpx.HTTPError as e:
                logger.error(e)
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2  # exponential backoff
                continue
            except KeyboardInterrupt as e:
                sys.exit(0)
            except Exception as e:
                logger.error(e)
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2  # exponential backoff
                continue

            json_data = response.json()
            if json_data and "error" not in json_data:
                # ok
                return json_data
            print(json_data)
            if not json_data:
                error_decription = "empty json data"
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2  # exponential backoff
                continue
            elif json_data["error_code"] == 16:
                await self.refresh_access_token()
                continue
                # goes to next iteration in retry loop
            else:
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2  # exponential backoff
                continue

        if error_decription == "" and "error_description" in json_data.keys():
            error_decription = json_data["error_description"]
        else:
            error_decription = "Unknown Error"

        raise PikpakException(error_decription)

    async def _request_get(self, url: str, params: dict = None, ):
        return await self._make_request("get", url, params=params)

    async def _request_post(self, url: str, data: dict = None, headers: dict = None, ):
        return await self._make_request("post", url, data=data, headers=headers)

    async def _request_patch(self, url: str, data: dict = None, ):
        return await self._make_request("patch", url, data=data)

    async def _request_delete(self, url: str, params: dict = None, data: dict = None, ):
        return await self._make_request("delete", url, params=params, data=data)

    def decode_token(self):
        """Decodes the encoded token to update access and refresh tokens."""
        try:
            decoded_data = json.loads(b64decode(self.encoded_token).decode())
        except (binascii.Error, json.JSONDecodeError):
            raise PikpakException("Invalid encoded token")
        if not decoded_data.get("access_token") or not decoded_data.get(
                "refresh_token"
        ):
            raise PikpakException("Invalid encoded token")
        self.access_token = decoded_data.get("access_token")
        self.refresh_token = decoded_data.get("refresh_token")

    def encode_token(self):
        """Encodes the access and refresh tokens into a single string."""
        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }
        self.encoded_token = b64encode(json.dumps(token_data).encode()).decode()

    async def captcha_init(self, action: str, meta: dict = None) -> Dict[str, Any]:
        url = f"https://{PikPakApi.PIKPAK_USER_HOST}/v1/shield/captcha/init"
        if not meta:
            t = f"{get_timestamp()}"
            meta = {
                "captcha_sign": captcha_sign(self.device_id, t),
                "client_version": CLIENT_VERSION,
                "package_name": PACKAG_ENAME,
                "user_id": self.user_id,
                "timestamp": t,
            }
        params = {
            "client_id": CLIENT_ID,
            "action": action,
            "device_id": self.device_id,
            "meta": meta,
        }
        return await self._request_post(url, data=params)

    async def login(self) -> None:
        """
        Login to PikPak
        """
        login_url = f"https://{PikPakApi.PIKPAK_USER_HOST}/v1/auth/signin"
        metas = {}
        if not self.username or not self.password:
            raise PikpakException("username and password are required")
        if re.match(r"\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", self.username):
            metas["email"] = self.username
        elif re.match(r"\d{11,18}", self.username):
            metas["phone_number"] = self.username
        else:
            metas["username"] = self.username
        result = await self.captcha_init(
            action=f"POST:{login_url}",
            meta=metas,
        )
        captcha_token = result.get("captcha_token", "")
        if not captcha_token:
            raise PikpakException("captcha_token get failed")
        login_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "password": self.password,
            "username": self.username,
            "captcha_token": captcha_token,
        }
        user_info = await self._request_post(login_url, login_data, {
            "Content-Type": "application/x-www-form-urlencoded",
        }, )
        self.access_token = user_info["access_token"]
        self.refresh_token = user_info["refresh_token"]
        self.user_id = user_info["sub"]
        self.encode_token()

    async def refresh_access_token(self) -> None:
        """
        Refresh access token
        """
        refresh_url = f"https://{self.PIKPAK_USER_HOST}/v1/auth/token"
        refresh_data = {
            "client_id": CLIENT_ID,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        user_info = await self._request_post(refresh_url, refresh_data)
        self.access_token = user_info["access_token"]
        self.refresh_token = user_info["refresh_token"]
        self.user_id = user_info["sub"]
        self.encode_token()

    def get_user_info(self) -> Dict[str, Optional[str]]:
        return {
            "username": self.username,
            "user_id": self.user_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "encoded_token": self.encoded_token,
        }

    async def get_upload_file(self, name, filesize, hashhex, ids="", parent_id=""):
        url = "https://api-drive.mypikpak.com/drive/v1/files"
        data = {
            "hash": hashhex.upper(),
            "name": name,
            "size": str(filesize),
            "kind": "drive#file",
            "id": ids,
            "parent_id": parent_id,
            "upload_type": "UPLOAD_TYPE_RESUMABLE",
            "folder_type": "NORMAL",
            "resumable": {"provider": "PROVIDER_ALIYUN"}
        }
        file_info = await self._request_post(url, data)
        return file_info

    async def create_folder(self, name: str = "新建文件夹", parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        name: str - 文件夹名称
        parent_id: str - 父文件夹id, 默认创建到根目录

        创建文件夹
        """
        url = f"https://{self.PIKPAK_API_HOST}/drive/v1/files"
        data = {
            "kind": "drive#folder",
            "name": name,
            "parent_id": parent_id,
        }
        result = await self._request_post(url, data)
        return result

    async def delete_to_trash(self, ids: List[str]) -> Dict[str, Any]:
        """
        ids: List[str] - 文件夹、文件id列表

        将文件夹、文件移动到回收站
        """
        url = f"https://{self.PIKPAK_API_HOST}/drive/v1/files:batchTrash"
        data = {"ids": ids, }
        result = await self._request_post(url, data)
        return result

    async def untrash(self, ids: List[str]) -> Dict[str, Any]:
        """
        ids: List[str] - 文件夹、文件id列表

        将文件夹、文件移出回收站
        """
        url = f"https://{self.PIKPAK_API_HOST}/drive/v1/files:batchUntrash"
        data = {"ids": ids, }
        result = await self._request_post(url, data)
        return result

    async def delete_forever(self, ids: List[str]) -> Dict[str, Any]:
        """
        ids: List[str] - 文件夹、文件id列表

        永远删除文件夹、文件, 慎用
        """
        url = f"https://{self.PIKPAK_API_HOST}/drive/v1/files:batchDelete"
        data = {"ids": ids, }
        result = await self._request_post(url, data)
        return result

    async def offline_download(self, file_url: str, parent_id: Optional[str] = None, name: Optional[str] = None) -> \
    Dict[str, Any]:
        """
        file_url: str - 文件链接
        parent_id: str - 父文件夹id, 不传默认存储到 My Pack
        name: str - 文件名, 不传默认为文件链接的文件名

        离线下载磁力链
        """
        download_url = f"https://{self.PIKPAK_API_HOST}/drive/v1/files"
        download_data = {
            "kind": "drive#file",
            "name": name,
            "upload_type": "UPLOAD_TYPE_URL",
            "url": {"url": file_url},
            "folder_type": "DOWNLOAD" if not parent_id else "",
            "parent_id": parent_id,
        }
        result = await self._request_post(download_url, download_data)
        return result

    async def offline_list(self, size: int = 10000, next_page_token: Optional[str] = None,
                           phase: Optional[List[str]] = None, ) -> Dict[str, Any]:
        """
        size: int - 每次请求的数量
        next_page_token: str - 下一页的page token
        phase: List[str] - Offline download task status, default is ["PHASE_TYPE_RUNNING", "PHASE_TYPE_ERROR"]
            supported values: PHASE_TYPE_RUNNING, PHASE_TYPE_ERROR, PHASE_TYPE_COMPLETE, PHASE_TYPE_PENDING

        获取离线下载列表
        """
        if phase is None:
            phase = ["PHASE_TYPE_RUNNING", "PHASE_TYPE_ERROR"]
        list_url = f"https://{self.PIKPAK_API_HOST}/drive/v1/tasks"
        list_data = {
            "type": "offline",
            "thumbnail_size": "SIZE_SMALL",
            "limit": size,
            "page_token": next_page_token,
            "filters": json.dumps({"phase": {"in": ",".join(phase)}}),
            "with": "reference_resource",
        }
        result = await self._request_get(list_url, list_data)
        return result

    async def offline_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        file_id: str - 离线下载文件id

        离线下载文件信息
        """
        url = f"https://{self.PIKPAK_API_HOST}/drive/v1/files/{file_id}"
        result = await self._request_get(url, {"thumbnail_size": "SIZE_LARGE"})
        return result

    async def file_list(self, size: int = 100, parent_id: Optional[str] = None, next_page_token: Optional[str] = None,
                        additional_filters: Optional[Dict[str, Any]] = None, ) -> Dict[str, Any]:
        """
        size: int - 每次请求的数量
        parent_id: str - 父文件夹id, 默认列出根目录
        next_page_token: str - 下一页的page token
        additional_filters: Dict[str, Any] - 额外的过滤条件

        获取文件列表，可以获得文件下载链接
        """
        default_filters = {
            "trashed": {"eq": False},
            "phase": {"eq": "PHASE_TYPE_COMPLETE"},
        }
        if additional_filters:
            default_filters.update(additional_filters)
        list_url = f"https://{self.PIKPAK_API_HOST}/drive/v1/files"
        list_data = {
            "parent_id": parent_id,
            "thumbnail_size": "SIZE_MEDIUM",
            "limit": size,
            "with_audit": "true",
            "page_token": next_page_token,
            "filters": json.dumps(default_filters),
        }
        result = await self._request_get(list_url, list_data)
        return result

    async def events(self, size: int = 100, next_page_token: Optional[str] = None) -> Dict[str, Any]:
        """
        size: int - 每次请求的数量
        next_page_token: str - 下一页的page token

        获取最近添加事件列表
        """
        list_url = f"https://{self.PIKPAK_API_HOST}/drive/v1/events"
        list_data = {
            "thumbnail_size": "SIZE_MEDIUM",
            "limit": size,
            "next_page_token": next_page_token,
        }
        result = await self._request_get(list_url, list_data)
        return result

    async def offline_task_retry(self, task_id: str) -> Dict[str, Any]:
        """
        task_id: str - 离线下载任务id

        重试离线下载任务
        """
        list_url = f"https://{self.PIKPAK_API_HOST}/drive/v1/task"
        list_data = {
            "type": "offline",
            "create_type": "RETRY",
            "id": task_id,
        }
        try:
            result = await self._request_post(list_url, list_data)
            return result
        except Exception as e:
            raise PikpakException(f"重试离线下载任务失败: {task_id}. {e}")

    async def delete_tasks(self, task_ids: List[str], delete_files: bool = False) -> None:
        """
        delete tasks by task ids
        task_ids: List[str] - task ids to delete
        """
        delete_url = f"https://{self.PIKPAK_API_HOST}/drive/v1/tasks"
        params = {
            "task_ids": task_ids,
            "delete_files": delete_files,
        }
        try:
            await self._request_delete(delete_url, params=params)
        except Exception as e:
            raise PikpakException(f"Failing to delete tasks: {task_ids}. {e}")

    async def path_to_id(self, path: str, create: bool = False) -> List[Dict[str, str]]:
        """
        path: str - 路径
        create: bool - 是否创建不存在的文件夹

        将形如 /path/a/b 的路径转换为 文件夹的id
        """
        if not path or len(path) <= 0:
            return []
        paths = path.split("/")
        paths = [p.strip() for p in paths if len(p) > 0]
        # 构造不同级别的path表达式，尝试找到距离目标最近的那一层
        multi_level_paths = ["/" + "/".join(paths[: i + 1]) for i in range(len(paths))]
        path_ids = [
            self._path_id_cache[p]
            for p in multi_level_paths
            if p in self._path_id_cache
        ]
        # 判断缓存命中情况
        hit_cnt = len(path_ids)
        if hit_cnt == len(paths):
            return path_ids
        elif hit_cnt == 0:
            count = 0
            parent_id = None
        else:
            count = hit_cnt
            parent_id = path_ids[-1]["id"]

        next_page_token = None
        while count < len(paths):
            current_parent_path = "/" + "/".join(paths[:count])
            data = await self.file_list(
                parent_id=parent_id, next_page_token=next_page_token
            )
            record_of_target_path = None
            for f in data.get("files", []):
                current_path = "/" + "/".join(paths[:count] + [f.get("name")])
                file_type = (
                    "folder" if f.get("kind", "").find("folder") != -1 else "file"
                )
                record = {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "file_type": file_type,
                }
                self._path_id_cache[current_path] = record
                if f.get("name") == paths[count]:
                    record_of_target_path = record
                    # 不break: 剩下的文件也同样缓存起来
            if record_of_target_path is not None:
                path_ids.append(record_of_target_path)
                count += 1
                parent_id = record_of_target_path["id"]
            elif data.get("next_page_token") and (
                    not next_page_token or next_page_token != data.get("next_page_token")
            ):
                next_page_token = data.get("next_page_token")
            elif create:
                data = await self.create_folder(name=paths[count], parent_id=parent_id)
                id = data.get("file").get("id")
                record = {
                    "id": id,
                    "name": paths[count],
                    "file_type": "folder",
                }
                path_ids.append(record)
                current_path = "/" + "/".join(paths[: count + 1])
                self._path_id_cache[current_path] = record
                count += 1
                parent_id = id
            else:
                break
        return path_ids

    async def file_batch_move(self, ids: List[str], to_parent_id: Optional[str] = None, ) -> Dict[str, Any]:
        """
        ids: List[str] - 文件id列表
        to_parent_id: str - 移动到的文件夹id, 默认为根目录

        批量移动文件
        """
        to = (
            {
                "parent_id": to_parent_id,
            }
            if to_parent_id
            else {}
        )
        result = await self._request_post(
            url=f"https://{self.PIKPAK_API_HOST}/drive/v1/files:batchMove",
            data={
                "ids": ids,
                "to": to,
            },
        )
        return result

    async def get_download_url(self, file_id: str) -> Dict[str, Any]:
        """
        id: str - 文件id

        Returns the file details data.
        1. Use `medias[0][link][url]` for streaming with high speed in streaming services or tools.
        2. Use `web_content_link` to download the file
        """
        result = await self.captcha_init(
            action=f"GET:/drive/v1/files/{file_id}",
        )
        self.captcha_token = result.get("captcha_token")
        result = await self._request_get(
            url=f"https://{self.PIKPAK_API_HOST}/drive/v1/files/{file_id}?",
        )
        self.captcha_token = None
        return result

    async def file_batch_share(self, ids: List[str], need_password: Optional[bool] = False,
                               expiration_days: Optional[int] = -1, ) -> Dict[str, Any]:
        """
        ids: List[str] - 文件id列表
        need_password: Optional[bool] - 是否需要分享密码
        expiration_days: Optional[int] - 分享天数

        批量分享文件，并生成分享链接
        返回数据结构：
        {
            "share_id": "xxx", //分享ID
            "share_url": "https://mypikpak.com/s/xxx", // 分享链接
            "pass_code": "53fe", // 分享密码
            "share_text": "https://mypikpak.com/s/xxx",
            "share_list": []
        }
        """
        data = {
            "file_ids": ids,
            "share_to": "encryptedlink" if need_password else "publiclink",
            "expiration_days": expiration_days,
            "pass_code_option": "REQUIRED" if need_password else "NOT_REQUIRED",
        }
        result = await self._request_post(url=f"https://{self.PIKPAK_API_HOST}/drive/v1/share", data=data, )
        return result

    async def get_quota_info(self) -> Dict[str, Any]:
        """
        获取当前空间的quota信息
        返回数据结构如下：
        {
            "kind": "drive#about",
            "quota": {
                "kind": "drive#quota",
                "limit": "10995116277760", //空间总大小， 单位Byte
                "usage": "5113157556024", // 已用空间大小，单位Byte
                "usage_in_trash": "1281564700871", // 回收站占用大小，单位Byte
                "play_times_limit": "-1",
                "play_times_usage": "0"
            },
            "expires_at": "",
            "quotas": {}
        }
        """
        result = await self._request_get(
            url=f"https://{self.PIKPAK_API_HOST}/drive/v1/about",
        )
        return result

    async def get_invite_code(self):
        result = await self._request_get(url=f"https://{self.PIKPAK_API_HOST}/vip/v1/activity/inviteCode", )
        return result["code"]

    async def vip_info(self):
        result = await self._request_get(url=f"https://{self.PIKPAK_API_HOST}/drive/v1/privilege/vip", )
        return result

    async def get_transfer_quota(self) -> Dict[str, Any]:
        """
        Get transfer quota
        """
        url = f"https://{self.PIKPAK_API_HOST}/vip/v1/quantity/list?type=transfer"
        result = await self._request_get(url)
        return result

    def upload(self, params, content):
        auth = oss2.StsAuth(params['access_key_id'], params['access_key_secret'], params["security_token"])
        bucket = oss2.Bucket(auth, params['endpoint'], params['bucket'])
        # a = bucket.put_object_from_file(params['key'], file_path)
        a = bucket.put_object(params['key'], content)
        print(a.headers)
        print(a.etag)
        print(a.resp)
        print(a.status)
        print(a.request_id)
        print(a.versionid)


async def main():
    # client = PikPakApi(username=None, password=None, encoded_token=encoded_token, httpx_client_args={
    #     # "proxy": "",
    #     "transport": httpx.AsyncHTTPTransport(retries=3),
    # })
    client = PikPakApi(username=username, password=password, encoded_token=None)

    await client.login()
    # await client.refresh_access_token()
    print(json.dumps(client.get_user_info(), indent=4))
    print("=" * 30, end="\n\n")
    print(await client.get_invite_code())
    print("=" * 30, end="\n\n")

    filename = filepath.split("\\")[-1]
    hashhex, content = calculate_sha1(filepath)
    data = await client.get_upload_file(filename, len(content), hashhex)
    params = data["resumable"]["params"]

    client.upload(params, content)

    print(json.dumps(await client.get_quota_info(), indent=4))
    print("=" * 30, end="\n\n")

    print(await client.get_invite_code())
    print("=" * 30, end="\n\n")

    print(json.dumps(await client.vip_info(), indent=4))
    print("=" * 30, end="\n\n")

    print(json.dumps(await client.get_transfer_quota(), indent=4))
    print("=" * 30, end="\n\n")


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

# 62953541 邀请码
