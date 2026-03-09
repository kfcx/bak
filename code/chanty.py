import json
import time
import uuid
import requests
from threading import Thread
from base64 import b64decode, b64encode
from requests.adapters import HTTPAdapter


class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.wss = None
        self.keep_running = True
        self.last_ping_time = None

    def keeplive(self, wss):
        while self.keep_running:
            time.sleep(1)
            current_time = int(time.time() * 1000)
            if self.last_ping_time is None or current_time - self.last_ping_time >= 5000:  # 每5秒发送一次ping
                self.send_message(f"ping:{current_time}")
                self.last_ping_time = current_time

    def on_open(self, wss):
        print("Connection opened")
        Thread(target=self.keeplive, args=(wss,)).start()

    def on_message(self, wss, message):
        print(f"Received message: {message}")
        data = json.loads(message)
        if data.get('eventType') == 'message_post':
            print("11111111")
            # self.post_message()

    def on_error(self, wss, error):
        print(f"Error: {error}")

    def on_close(self, wss, close_status_code, close_msg):
        print("Connection closed")
        self.keep_running = False

    def on_pong(self, wss, message):
        print(f"Received Pong message: {message}")

    def on_ping(self, wss, message):
        print(f"Received Pong message: {message}")

    def run(self):
        while self.keep_running:
            try:
                headers = {
                    "Accept": "*/*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
                }
                self.wss = websocket.WebSocketApp(self.url,
                                                  header=headers,
                                                  on_open=self.on_open,
                                                  on_message=self.on_message,
                                                  on_error=self.on_error,
                                                  on_close=self.on_close)
                # self.wss.on_pong = self.on_pong
                # self.wss.on_ping = self.on_ping
                # self.wss.run_forever(ping_interval=5, ping_timeout=3)
                self.wss.run_forever()
            except Exception as e:
                print(f"Exception: {e}")
                time.sleep(5)  # Wait before reconnecting

    def send_message(self, message):
        if self.wss and self.wss.sock and self.wss.sock.connected:
            self.wss.send(message)
        else:
            print("WebSocket is not connected.")

    def start(self):
        self.keep_running = True
        t = Thread(target=self.run)
        t.setDaemon(True)
        t.start()

    def stop(self):
        self.keep_running = False
        if self.wss:
            self.wss.close()


class Chanty(WebSocketClient):
    def __init__(self):
        adapter = HTTPAdapter(max_retries=3)
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.data = {
            "token": "",
            "tokenExpire": "28800",
            "refreshToken": "",
            "jid": "@.chanty.com",
            "name": "",
            "domain": ".chanty.com",
            "storageVars": {"Policy": "", "Key-Pair-id": "", "Signature": ""},
            "ws": "wss://rt-aws-u1.chanty.com/ws",
        }
        self.headers = {
            "Host": ".chanty.com",
            "User-Agent": "Chanty/45564 CFNetwork/1329 Darwin/21.3.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"bearer {self.data['token']}",
            "Origin": "https://.chanty.com",
            "Connection": "keep-alive",
        }
        wss_url = f"{self.data['ws']}?token={self.data['token']}&jid={self.data['jid']}"
        super().__init__(wss_url)  # 调用父类的构造函数
        # 发送消息到1005创建新连接
        print(wss_url)
        self.wss_client = WebSocketClient(wss_url)
        self.wss_client.start()

    def post_message(self, message, attachments):
        url = "https://.chanty.com/api/v1/message/post"
        data = {
            # "team": "",
            "tempId": str(uuid.uuid4()),
            "convJid": "general@.chanty.com",
            "convType": "channel",
            "text": message,
            "attachments": attachments,
            # "attachments": [],
            "richContent": "",
            "replyId": "",
            "scheduleOn": None,
            "action": "set"
        }
        with requests.post(url=url,
                           headers=dict(self.headers, **{"Referer": "https://.chanty.com/app/channel/general"}),
                           json=data) as resp:
            print(resp.status_code)
            print(resp.headers)
            print(resp.text)

    def upload(self, filename, filedata, message=""):
        print(f"filename={filename}, filelen={len(filedata)}, message={message}")
        url = "https://.chanty.com/api/v1/media/upload"
        mine = ["application/octet-stream", "video/vnd.dlna.mpeg-tts", "video/mp4", "text/plain",
                "application/x-javascript"]
        data = {
            "file": filename,
            "mime": "video/mp4",
            # "mime": "text/plain",
            "size": 1024 * 1024 * 99 if len(filedata) > 1024 * 1024 * 100 else len(filedata),
            "res": "conversation",  # codesnippet代码
            "head": b64encode(filedata[:1024] if len(filedata) > 1024 else filedata).decode(),
            # "team": "",
            # "action": "set"
        }
        with requests.post(url=url,
                           headers=dict(self.headers, **{"Referer": "https://.chanty.com/app/channel/general"}),
                           json=data) as resp:
            print(resp.status_code)
            content = resp.json()
            print(content)
            print(content["status"])
            if content["status"] == False:
                print("上传失败", resp.text)
                return False
        url = content["data"]["url"]
        data = {
            "key": content["data"]["params"]["key"],
            "acl": content["data"]["params"]["acl"],
            "success_action_status": content["data"]["params"]["success_action_status"],
            "content-type": content["data"]["params"]["content-type"],
            "Content-Disposition": content["data"]["params"]["Content-Disposition"],
            "tagging": content["data"]["params"]["tagging"],
            "bucket": content["data"]["params"]["bucket"],
            "X-Amz-Algorithm": content["data"]["params"]["X-Amz-Algorithm"],
            "X-Amz-Credential": content["data"]["params"]["X-Amz-Credential"],
            "X-Amz-Date": content["data"]["params"]["X-Amz-Date"],
            "Policy": content["data"]["params"]["Policy"],
            "X-Amz-Signature": content["data"]["params"]["X-Amz-Signature"],
            "file": (filename, filedata),
        }
        return self.s3_post(url, data)

    def s3_post(self, url, data):
        print(url.split("/")[2])
        headers = {
            "Host": url.split("/")[2],
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://.chanty.com",
            # "Origin": "capacitor://localhost",
            "Connection": "keep-alive",
        }
        with requests.post(url=url, headers=headers, files=data) as resp:
            print(resp.status_code)
            print(resp.text)
            location = resp.headers["Location"]
            print(location)  # url+data["key"]
        attachments = [
            {"app": "",
             "dimensions": [],
             "loader": "",
             "mime": "",  # text/plain
             "preview": "",
             "previewCSS": "",
             "icon": "",
             "description": "",
             "type": "upload",  # codesnippet
             "orientation": 1,
             "size": 0,
             "id": "",
             "messageId": "",
             "name": data["file"][0],
             "uri": location,
             "url": "",
             "source": "upload",
             "oembed": "",
             "mode": "",  # text/x-python
             "modeName": "",  # Python
             "title": "",
             "target": "",
             "waveform": [],
             "createdOn": None,
             "finishedOn": None,
             "startedOn": None,
             "finishedReason": "",
             "lasted": 0,
             "providerName": None,
             "range": False,
             "showMoreContentDefault": False,
             "isDetachOn": False,
             "isDetached": False,
             "placeHolder": None,
             "attachmentPlay": None,
             "showInPopup": None,
             "iframeSrc": "",
             "oembedInstanceId": ""
             }]
        return attachments

    def get_auth(self):
        url = "https://.chanty.com/api/v1/user/auth/get"
        data = {"platform": "web", "os": "Windows", "version": "0.29.3", "navigator": "5.0 (Windows)"}
        with self.session.post(url=url, headers=self.headers, json=data) as resp:
            print(resp.status_code)
            if resp.status_code == 401:
                return self.get_token()
            print(resp.headers)
            print(resp.text)

    def get_token(self):
        url = "https://.chanty.com/api/v1/user/auth/token"
        data = {
            "platform": "web",
            "token": self.data['refreshToken'],
            "jid": self.data["jid"],
            "action": "set",
            "os": "Windows",
            "version": "0.29.3",
            "navigator": "5.0 (Windows)"
        }
        with self.session.post(url=url, headers=self.headers, json=data) as resp:
            print(resp.status_code)
            if resp.status_code == 401:
                print("刷新token失效，请重新登录")
                raise Exception("获取token失败")
            print(resp.headers)
            print(resp.text)
            return resp.json()


def main():
    chanty = Chanty()
    while True:
        time.sleep(1)
        text = input("输入c")
        if text == "c":
            chanty.stop()
            break
        if text == "p":
            message = "new"
            attachments = chanty.upload(filename, filedata, message)
            input("上传完成，等待信息")
            # message = attachments[0]["uri"]
            if attachments:
                chanty.post_message(message, attachments)


if __name__ == "__main__":
    main()

