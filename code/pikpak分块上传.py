import asyncio
import hashlib
import json
import os.path
import sys
import threading
import time
import boto3
import oss2
from loguru import logger
from pikpakapi import PikPakApi, PikpakException
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
from functools import lru_cache

lock = threading.Lock()
false = False
true = True
null = None
PART_SIZE = 10 * 1024 * 1024


@lru_cache()
def get_redis():
    import redis
    cache_redis_url = ""
    redis = redis.from_url(cache_redis_url,
                           encoding='utf-8',
                           decode_responses=True,
                           health_check_interval=60,
                           socket_connect_timeout=True,
                           retry_on_timeout=True,
                           socket_keepalive=True)
    return redis


class Bucket:
    def __init__(self, bucket_name=""):
        aws_access_key_id = ''
        aws_secret_access_key = ''
        endpoint_url = 'https://s3'

        self.s3 = boto3.resource(
            service_name='s3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            config=Config(signature_version='s3v4')
        )
        self.bucket = self.s3.Bucket(bucket_name)

    def put(self, key, data):
        return self.bucket.put_object(Key=key, Body=data)

    def put_json(self, key: str, data: dict):
        json_data = json.dumps(data)
        return self.put(key, json_data)

    def get(self, key):
        return self.bucket.Object(key).get()['Body'].read()

    def get_json(self, key):
        json_data = json.loads(self.get(key))
        return json_data

    def list(self):
        return [obj.key for obj in self.bucket.objects.all()]

    def delete(self, key):
        return self.bucket.Object(key).delete()

    def upload_file_in_parts2(self, file_path, object_name, part_size=PART_SIZE):
        multipart_upload = self.bucket.Object(object_name).initiate_multipart_upload()
        print(multipart_upload)

        parts = []
        part_number = 1

        try:
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(part_size)
                    if not data:
                        break
                    part = multipart_upload.Part(part_number)
                    response = part.upload(Body=data)
                    parts.append({
                        'PartNumber': part_number,
                        'ETag': response['ETag']
                    })
                    print(parts)
                    part_number += 1

            multipart_upload.complete(MultipartUpload={'Parts': parts})
            print(f"File {file_path} uploaded successfully as {object_name}.")
        except Exception as e:
            multipart_upload.abort()
            print(f"An error occurred: {e}")

    def _mupload(self, s3mupload, counter, part_size, data, handle):
        part = s3mupload.Part(counter)
        response = part.upload(Body=data[part_size * (counter-1):part_size * counter])
        with lock:
            handle.write(json.dumps({'PartNumber': counter, 'ETag': response['ETag']}) + "\n")
        return counter, response['ETag']

    def multipart_upload(self, content, object_name, part_size=PART_SIZE):
        filename = os.path.splitext(object_name)[0]
        parts = []
        if os.path.exists(filename):
            with open(filename, "r") as handle:
                _ = handle.read()
                _flag1 = _.count("upload_id=")
                _flag2 = _.count("PartNumber")
                _ = _.split("\n")
                if _flag1:
                    upload_id = _[0].split("=")[-1]
                if _flag2:
                    parts.extend([json.loads(i) for i in _[1:] if i])
                    print(parts)
            s3mupload = self.s3.MultipartUpload(bucket_name=self.bucket.name, object_key=object_name, id=upload_id)
        else:
            s3mupload = self.bucket.Object(object_name).initiate_multipart_upload()
            with open(filename, "w") as fp:
                fp.write(f"upload_id={s3mupload.id}\n")
        print(s3mupload)
        total_size = len(content)
        counter = total_size // part_size
        _ = [int(i['PartNumber']) for i in parts]
        going = [i for i in range(counter) if i + 1 not in _]
        print(going)
        with open(filename, "a+") as handle:
            if counter > 0:
                logger.info("正在上传分片")
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = {executor.submit(self._mupload, s3mupload, i+1, part_size, content, handle, ): i for i in going}
                    for future in futures:
                        x, etag = future.result()
                        logger.info(f"已上传分片 {x} {etag}")
                        parts.append({'PartNumber': x, 'ETag': etag})
            if total_size % part_size != 0 and len(parts) != counter+1:  # 最后分片未上传，并且有数据
                logger.info("正在上传最后一个分片")
                part = s3mupload.Part(counter + 1)
                response = part.upload(Body=content[-(total_size % part_size):])
                handle.write(json.dumps({'PartNumber': counter, 'ETag': response['ETag']}) + "\n")
                parts.append({'PartNumber': counter + 1, 'ETag': response['ETag']})
        parts.sort(key=lambda x: x['PartNumber'])
        s3mupload.complete(MultipartUpload={'Parts': parts})
        print(f"File uploaded successfully as {object_name}.")
        # s3mupload.abort()


def calculate_sha1(filepath, chunk_size=PART_SIZE):
    # content list ? 每个都和要分片上传的大小一致？
    sha1 = hashlib.sha1()
    content = b""
    with open(filepath, "rb") as fp:
        while chunk := fp.read(chunk_size):
            sha1.update(chunk)
            content += chunk
    return sha1.hexdigest(), content


class Pikpak:
    # ali auth授权源码
    # https://github.com/aliyun/aliyun-oss-python-sdk/blob/master/oss2/auth.py#L77
    def __init__(self, username=None, password=None):
        self.token = {
            "expire": int(time.time()) + 7200,  # nowtime + 7200
            # "expire": 1727347906 + 7200,  # nowtime + 7200
            "username": "moislooky@outlook.com",
            "user_id": "ZrnDHT703Jv6b-3a",
            "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImI3NTMxOTJhLTEwYTgtNDNjZC1hM2Q1LWJiNWQ0MjRhYTIzZiJ9.eyJpc3MiOiJodHRwczovL3VzZXIubXlwaWtwYWsuY29tIiwic3ViIjoiWnJuREhUNzAzSnY2Yi0zYSIsImF1ZCI6IllOeFQ5dzdHTWRXdkVPS2EiLCJleHAiOjE3NzI5ODE1OTEsImlhdCI6MTc3Mjk3NDM5MSwiYXRfaGFzaCI6InIuVDY3OVFnMWdRd3FKcWZkTlJFVFRVQSIsInNjb3BlIjoidXNlciBwYW4gc3luYyBvZmZsaW5lIiwicHJvamVjdF9pZCI6IjJ3a3M1NmMzMWRjODBzeG01cDkiLCJtZXRhIjp7ImEiOiJla0pGNnZmdmtPSmJ0S2tOaURwRnBoK1VQV2RFWk91ellLKzIyQlZLUkFVPSJ9fQ.0kgoy1LyM155V5fnqe4WHa8cn4d_i4yJyA-I4JLEjTVw3sxM20kAYGUNOZCfr5MINyLDYWcEcOIU1gP95IyJdPP1bHf3wdx2_EPgBcsgB-ilPgimaWIqthxI1huyTC1D36YKwdHSVaq4Q5FZNMKMexCsFv0c85pFWxTXigiYSyeTkvhFApNMZmUcU7oZhFQawrhadwtALhx-K6gz_MTIS7-7Jk6PsodN_mDk_PSexYARMm8SprRKL7bE5ZrNsptD1OCkIbsTuXTKmCB8cDArXAYZqizvBQmUBDflzTBoiCjYpZfDgHqgho8zD-4LHiXHXA5_rQeS5r3mDbaw8umMRg",
            "refresh_token": "os.I9CV-nWMbWmtcTcWPhA6ov01PSU9IZK9OPsooiz1lpM1v7MzjyQrCY6a4IZc",
            "encoded_token": "eyJhY2Nlc3NfdG9rZW4iOiAiZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkltSTNOVE14T1RKaExURXdZVGd0TkROalpDMWhNMlExTFdKaU5XUTBNalJoWVRJelppSjkuZXlKcGMzTWlPaUpvZEhSd2N6b3ZMM1Z6WlhJdWJYbHdhV3R3WVdzdVkyOXRJaXdpYzNWaUlqb2lXbkp1UkVoVU56QXpTblkyWWkwellTSXNJbUYxWkNJNklsbE9lRlE1ZHpkSFRXUlhka1ZQUzJFaUxDSmxlSEFpT2pFM056STVPREUxT1RFc0ltbGhkQ0k2TVRjM01qazNORE01TVN3aVlYUmZhR0Z6YUNJNkluSXVWRFkzT1ZGbk1XZFJkM0ZLY1daa1RsSkZWRlJWUVNJc0luTmpiM0JsSWpvaWRYTmxjaUJ3WVc0Z2MzbHVZeUJ2Wm1ac2FXNWxJaXdpY0hKdmFtVmpkRjlwWkNJNklqSjNhM00xTm1Nek1XUmpPREJ6ZUcwMWNEa2lMQ0p0WlhSaElqcDdJbUVpT2lKbGEwcEdOblptZG10UFNtSjBTMnRPYVVSd1JuQm9LMVZRVjJSRldrOTFlbGxMS3pJeVFsWkxVa0ZWUFNKOWZRLjBrZ295MUx5TTE1NVY1Zm5xZTRXSGE4Y240ZF9pNHlKeUEtSTRKTEVqVFZ3M3N4TTIwa0FZR1VOT1pDZnI1TUlOeUxEWVdjRWNPSVUxZ1A5NUl5SmRQUDFiSGYzd2R4Ml9FUGdCY3NnQi1pbFBnaW1hV0lxdGh4STFodXlUQzFEMzZZS3dkSFNWYXE0UTVGWk5NS01leENzRnYwYzg1cEZXeFRYaWdpWVN5ZVRrdmhGQXBOTVptVWNVN29aaEZRYXdyaGFkd3RBTGh4LUs2Z3pfTVRJUzctN0prNlBzb2ROX21Ea19QU2V4WUFSTW04U3ByUktMN2JFNVpyTnNwdEQxT0NrSWJzVHVYVEttQ0I4Y0RBclhBWVpxaXp2QlFtVUJEZmx6VEJvaUNqWXBaZkRnSHFnaG84ekQtNExIaVhIWEE1X3JRZVM1cjNtRGJhdzh1bU1SZyIsICJyZWZyZXNoX3Rva2VuIjogIm9zLkk5Q1YtbldNYldtdGNUY1dQaEE2b3YwMVBTVTlJWks5T1Bzb29pejFscE0xdjdNemp5UXJDWTZhNElaYyJ9"
        }
        self.client = PikPakApi(username=username, password=password, encoded_token=self.token["encoded_token"])
        # self.client = None
        self.username = username
        self.password = password

    async def execute(self, name, filesize, hashhex, ids="", parent_id="VO7iIdseIqovt1FlC-6aZUDIo1"):
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
        logger.debug("正在获取上传参数")

        backoff_seconds = 3
        error_decription = ""
        client = await self.get_pikpak_client()
        # parent_folder = await client.path_to_id(save_path, create=True)   #先获取父文件夹

        for i in range(3):
            req_headers = client.get_headers()
            try:
                response = await client.httpx_client.request("post", url, json=data, headers=req_headers, )
                print(response.status_code)
            except KeyboardInterrupt as e:
                sys.exit(0)
            except Exception as e:
                logger.error(e)
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2  # exponential backoff
                continue

            json_data = response.json()
            if json_data and "error" not in json_data:  # ok
                return json_data

            if not json_data:
                error_decription = "empty json data"
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2  # exponential backoff
                continue
            elif json_data["error_code"] == 16:
                await client.refresh_access_token()
                self.token["expire"] = int(time.time()) + 7200
                _ = self.client.get_user_info()
                if self.token["refresh_token"] != _["refresh_token"]:
                    print(json.dumps(self.client.get_user_info(), indent=4))
                continue
                # goes to next iteration in retry loop
            else:
                print(json.dumps(json_data, indent=4))
                error_decription = json_data["error_description"]
                await asyncio.sleep(backoff_seconds)
                backoff_seconds *= 2  # exponential backoff
                continue

        raise PikpakException(error_decription)

    async def execute3(self, name, filesize, hashhex, ids="", parent_id=""):
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
        logger.debug("正在请求上传")

        client = await self.get_pikpak_client()
        # parent_folder = await client.path_to_id(save_path, create=True)   #先获取父文件夹
        info = await client._request_post(url, data)
        print(info)
        return info

    async def get_pikpak_client(self) -> PikPakApi:
        """
        获取 PikPak 实例, 从缓存中读取 token
        """
        if self.client:
            # 60 分钟刷新一次 token
            if self.token["expire"] and int(time.time()) + 60 < self.token["expire"]:
                return self.client
            try:
                logger.warning("token失效，正在重新获取")
                await self.client.refresh_access_token()
                self.token["expire"] = int(time.time()) + 7200
                _ = self.client.get_user_info()
                if self.token["refresh_token"] != _["refresh_token"]:
                    print(json.dumps(self.client.get_user_info(), indent=4))
                return self.client
            except Exception as e:
                logger.debug(f"PikPak refresh token 失败: {e}")
        try:
            self.client = PikPakApi(username=self.username, password=self.password, )
            refresh_token = self.token["refresh_token"]
            if refresh_token:
                self.client.refresh_token = refresh_token
                try:
                    logger.warning("token失效，正在重新获取")
                    await self.client.refresh_access_token()
                    _ = self.client.get_user_info()
                    if self.token["refresh_token"] != _["refresh_token"]:
                        print(json.dumps(self.client.get_user_info(), indent=4))
                    return self.client
                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    logger.debug(f"PikPak refresh token 失败: {e}")
            logger.warning("refresh token失效，正在重新登录")
            await self.client.login()
            return self.client
        finally:
            if self.client and self.client.refresh_token:
                self.token["refresh_token"] = self.client.refresh_token
                _ = self.client.get_user_info()
                if self.token["refresh_token"] != _["refresh_token"]:
                    print(json.dumps(self.client.get_user_info(), indent=4))

    def single_upload(self, params, content):
        auth = oss2.StsAuth(params['access_key_id'], params['access_key_secret'], params["security_token"])
        # bucket = oss2.Bucket(auth, params['endpoint'], params['bucket'])
        bucket = oss2.Bucket(auth, "mypikpak.com", params['bucket'])
        # a = bucket.put_object_from_file(params['key'], file_path)
        a = bucket.put_object(params['key'], content)
        print(a.status)
        print(a.request_id)

    def multipart_upload2(self, params, content, part_size=PART_SIZE):
        total_size = len(content)
        object_name = params["key"]
        auth = oss2.StsAuth(params['access_key_id'], params['access_key_secret'], params["security_token"])
        bucket = oss2.Bucket(auth, "mypikpak.com", params['bucket'])

        upload_id = bucket.init_multipart_upload(object_name).upload_id
        print(upload_id)
        parts = []

        counter = total_size // part_size
        for i, x in enumerate([part_size for _ in range(counter)]):
            logger.info(f"正在上传 {i} {part_size}")
            part = bucket.upload_part(object_name, upload_id, i + 1, content[part_size * i:part_size * (i + 1)])
            print(i + 1, part.etag)
            parts.append(oss2.models.PartInfo(i + 1, part.etag))
        logger.info("已上传完大半")
        part = bucket.upload_part(object_name, upload_id, counter + 1, content[-(total_size % part_size):])
        parts.append(oss2.models.PartInfo(counter + 1, part.etag))

        bucket.complete_multipart_upload(object_name, upload_id, parts)
        print(f"File uploaded successfully as {object_name}.")

    def _mupload(self, bucket, object_name, upload_id, counter, part_size, content, handle):
        part = bucket.upload_part(object_name, upload_id, counter, content[part_size * (counter-1):part_size * counter])
        with lock:
            handle.write(f"{counter}@@{part.etag}\n")
        return counter, part.etag

    def multipart_upload(self, params, content, filename, part_size=PART_SIZE):
        filename = os.path.splitext(filename)[0]
        if os.path.exists("video/"+filename):
            with open("video/"+filename, "r") as handle:
                _ = handle.read()
                _flag1 = _.count("upload_id=")
                _flag2 = _.count("@@")
                _ = _.split("\n")
                data = {}
                if _flag1:
                    data["upload_id"] = _[1].split("=")[-1]
                if _flag2:
                    data["parts"] = [oss2.models.PartInfo(*i.split("@@")) for i in _[2:] if i]
        else:
            data = {}

        total_size = len(content)
        counter = total_size // part_size
        object_name = params["key"]
        auth = oss2.StsAuth(params['access_key_id'], params['access_key_secret'], params["security_token"])
        bucket = oss2.Bucket(auth, "mypikpak.com", params['bucket'])
        parts = data.get("parts", [])
        _ = [int(i.part_number) for i in parts]
        going = [i for i in range(counter) if i + 1 not in _]
        with open("video/"+filename, "a+") as handle:
            if data.get("upload_id"):
                upload_id = data.get("upload_id")
            else:
                upload_id = bucket.init_multipart_upload(object_name).upload_id
                handle.write(f"upload_id={upload_id}\n")
            if counter > 0:
                logger.info("正在上传分片")
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {executor.submit(self._mupload, bucket, object_name, upload_id, i + 1, part_size, content, handle, ): i for i in going}
                    for future in futures:
                        x, etag = future.result()
                        logger.info(f"已上传分片 {x} {etag}")
                        parts.append(oss2.models.PartInfo(x, etag))

            if total_size % part_size != 0 and len(parts) != counter+1:  # 最后分片未上传，并且有数据
                logger.info("正在上传最后一个分片")
                part = bucket.upload_part(object_name, upload_id, counter + 1, content[-(total_size % part_size):])
                parts.append(oss2.models.PartInfo(counter + 1, part.etag))
                handle.write(f"{counter + 1}@@{part.etag}\n")
        bucket.complete_multipart_upload(object_name, upload_id, parts)
        print(f"File uploaded successfully as {object_name}.")


async def main():
    os.makedirs("video", exist_ok=True)
    # bucket = Bucket()
    # filename = os.path.splitext(filename)[0]
    # with open(filepath, "rb") as fp:
    #     content = fp.read()
    # bucket.multipart_upload(content, f"video/{filename}.mp4")

    # print(dir(bucket.bucket))
    print(time.time())
    pikpak = Pikpak(username, password)

    filename = filepath.split("\\")[-1]
    filename = os.path.splitext(filename)[0]

    hashhex, content = calculate_sha1(filepath)
    if os.path.exists("video/"+filename):
        with open("video/"+filename, "r") as handle:
            _ = handle.read().split("\n")
            params = json.loads(_[0])
    else:
        data = await pikpak.execute(filename, len(content), hashhex)
        params = data["resumable"]["params"]
        with open("video/"+filename, "w") as handle:
            handle.write(json.dumps(params) + "\n")
        print(json.dumps(data))
        print(json.dumps(pikpak.client.get_user_info(), indent=4))
    if params:
        # pikpak.upload(params, content)
        pikpak.multipart_upload(params, content, filename)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
