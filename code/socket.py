# -*- coding: utf-8 -*-
# @Time    : 2023/3/26
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : socket.py
# @Software: PyCharm

import asyncio
import json
import random
import urllib.parse

import aiohttp
import websockets


class WebSocketStatus:
    connecting = 0
    open = 1
    closing = 2
    closed = 3


class WebSocketClient1:
    def __init__(self, settings):
        self._settings = settings
        self._socket = None
        self._back_off_time = 1000
        self._min_seq = settings["minSeq"]
        self._channel = settings["channel"]
        self._channel_hash = settings["channelHash"]
        self._box_name = settings["boxName"]
        self._base_host = settings["baseHost"]
        self._target_url = settings["targetUrl"]
        self._pbCookie = settings["quora_cookie"]
        self._online = True
        self._callbacks = {}
        self._websocket_status = WebSocketStatus.closed

    def _reset_back_off_time(self):
        self._back_off_time = 1000

    def _update_back_off_time(self):
        self._back_off_time = min(2 * self._back_off_time, 60000)

    async def _fetch_settings(self):
        # Assuming that `a.Bj()` is a function that returns a coroutine that fetches settings
        # using some API, we can replace it with aiohttp or requests.
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://poe.com/api/settings?channel={self._channel}',
                                   headers={'cookie': self._pbCookie}) as setting:
                if setting.status != 200:
                    raise Exception("Failed to fetch token")
                settings = await setting.json()
        return settings["tchannelData"]

    async def _refetch_settings_and_reconnect(self):
        self._close_web_socket()
        settings = await self._fetch_settings()
        print(settings)
        self._min_seq = settings['minSeq']
        self._channel = settings['channel']
        self._channel_hash = settings['channelHash']
        self._box_name = settings['boxName']
        self._base_host = settings['baseHost']
        self._target_url = self._make_target_url(self._base_host, self._box_name, settings['targetUrl'])
        self._callbacks.pop('missed_messages', None)

        await self._connect_web_socket()

    def _on_error(self):
        asyncio.get_event_loop().call_later(self._back_off_time / 1000, self._update_back_off_time)
        asyncio.get_event_loop().call_later(self._back_off_time / 1000, self._connect_web_socket)

    def _on_received_response(self, response):
        self._reset_back_off_time()

        if response.get('error') == 'missed_messages':
            asyncio.get_event_loop().create_task(self._refetch_settings_and_reconnect())
            return

        if response.get('error'):
            raise ValueError(response.get('error'))

        for message in response.get('messages', []):
            message_type = message.get('message_type')
            if message_type in self._callbacks:
                self._callbacks[message_type](message.get('payload'))

        self._min_seq = str(response.get('min_seq'))

    async def _send_request(self, message_type, payload):
        if not self._socket or self._socket.closed:
            await self._connect_web_socket()

        while self._websocket_status == WebSocketStatus.connecting:
            await asyncio.sleep(0.1)

        if self._websocket_status == WebSocketStatus.closed:
            raise ConnectionError('WebSocket is closed')

        request = {
            'message_type': message_type,
            'payload': payload
        }
        await self._socket.send(json.dumps(request))

    async def _handle_message(self, message):
        try:
            response = json.loads(message)
        except json.JSONDecodeError:
            return

        if not isinstance(response, dict):
            return

        if 'error' in response:
            self._on_received_response(response)
        elif 'message_type' in response and 'payload' in response:
            message_type = response['message_type']
            if message_type in self._callbacks:
                self._callbacks[message_type](response['payload'])

    async def _connect_web_socket(self):
        if not self._online:
            return

        if self._socket and not self._socket.closed:
            return

        self._websocket_status = WebSocketStatus.connecting
        self._reset_back_off_time()

        self._socket = None
        query_params = {
            'min_seq': str(self._min_seq),
            'channel': self._channel,
            'hash': self._channel_hash
        }
        url = self._make_target_url(self._base_host, self._box_name,
                                    self._settings['targetUrl']) + '/up/' + urllib.parse.urlencode(query_params)
        print(url)
        try:
            self._socket = await websockets.connect(url)
        except Exception as exc:
            print(f'Error connecting to WebSocket: {exc}')
            self._on_error()
            return

        self._websocket_status = WebSocketStatus.open
        self._socket.on_message = self._handle_message

    # def _close_web_socket(self):
    #     if self._socket and not self._socket.closed:
    #         self.

    def _close_web_socket(self):
        if self._socket and not self._socket.closed:
            try:
                asyncio.get_event_loop().create_task(self._socket.close())
            except Exception as exc:
                print(f'Error closing WebSocket: {exc}')
            finally:
                self._socket = None

    def start(self):
        asyncio.get_event_loop().create_task(self._refetch_settings_and_reconnect())
        asyncio.get_event_loop().create_task(self._connect_web_socket())

    def stop(self):
        self._online = False
        if self._socket and not self._socket.closed:
            asyncio.get_event_loop().create_task(self._socket.close())

    def reconnect(self):
        self._close_web_socket()
        asyncio.get_event_loop().create_task(self._connect_web_socket())

    async def check_connection(self):
        if not self._socket or self._socket.closed:
            self.reconnect()

    def _make_target_url(self, base_host, box_name, target_url):
        return f'wss://{base_host}/tch/{box_name}/up/{target_url}'

    def add_callback(self, message_type, callback):
        if message_type not in self._callbacks:
            self._callbacks[message_type] = []
        self._callbacks[message_type].append(callback)

    def remove_callback(self, message_type, callback):
        if message_type in self._callbacks:
            self._callbacks[message_type] = [cb for cb in self._callbacks[message_type] if cb != callback]
            if not self._callbacks[message_type]:
                self._callbacks.pop(message_type)

    async def send_message(self, message_type, payload):
        await self._send_request(message_type, payload)


async def handle_message(message_type, payload):
    print(f'Received message of type {message_type}: {payload}')


async def main():
    with open("config.json") as f:
        config = json.load(f)
    # Create a new instance of the WebSocketClient class
    client = WebSocketClient1({"quora_cookie": config["quora_cookie"],**config["app_settings"]["tchannelData"]})

    # Register a message callback function
    client.add_callback('my_message_type', handle_message)

    # Connect to the WebSocket server
    client.start()

    # Send a message to the WebSocket server
    payload = {'foo': 'bar'}
    await client.send_message('my_message_type', payload)

    # Wait for 10 seconds for messages to be received
    await asyncio.sleep(10)

    # Disconnect from the WebSocket server
    client.stop()


if __name__ == '__main__':
    asyncio.run(main())
