# -*- coding: utf-8 -*-
# @Time    : 2023/3/20
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : wss连接.py
# @Software: PyCharm
import atexit
import json
import websocket
import threading
import time


class WssClient:
    def __init__(self, url, headers=None, timeout=30):
        self.url = url
        self.ws = None
        self.headers = headers
        self.is_connected = False
        # self.receive_messages = Queue()
        self.received_flag = True
        self.timeout = timeout
        self.lock = threading.Lock()

    def start(self, enableTrace=False):
        websocket.enableTrace(enableTrace)
        self.ws = websocket.WebSocketApp(self.url,
                                         header=self.headers,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

    def on_open(self, ws):
        self.is_connected = True
        print("WebSocket connection opened")
        threading.Thread(target=self.send_message_loop).start()  # 启动一个线程定时发送消息

    def on_message(self, ws, message):
        if message == "PONG":
            return
        with self.lock:
            message = json.loads(message)["content"]
            if message == "[DONE]":
                self.received_flag = True
                print()
            else:
                print(message, end="", flush=True)

    def on_error(self, ws, error):
        print("WebSocket error: {}".format(error))

    def on_close(self, ws, *args):
        self.is_connected = False
        if self.is_connected:
            ws.close()
            print("WebSocket connection closed")

    def send_message(self, message):
        with self.lock:
            if self.is_connected:
                self.ws.send(json.dumps(message))

    def send_message_loop(self):
        while self.is_connected:
            self.send_message("ping")
            time.sleep(self.timeout)


if __name__ == "__main__":
    url = "wss://chatgpt.xyb.com/chat"
    headers = {
        "Host": "chatgpt.xyb.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "*/*",
        # "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-WebSocket-Version": "13",
        "Origin": "https://xyb.com",
        # "Sec-WebSocket-Extensions": "permessage-deflate",
        "Connection": "keep-alive, Upgrade",
    }
    client = WssClient(url, headers, 10)
    atexit.register(client.on_close, client.ws)
    threading.Thread(target=client.start).start()

    # 向服务器发送消息
    while True:
        time.sleep(1)
        # with client.lock:
        text = input("问：" if client.received_flag else "")
        if text:
            if text == "exit":
                break
            client.received_flag = False
            print("答：", end="")
            client.send_message({
                "content": text,
                "session": "6d2497ef0bfe4b2d08cb5b3a75ae762f0a6bb329f59576dc0d311ebcccf04df8"
            })

    # 断开WebSocket连接
    client.ws.close()
