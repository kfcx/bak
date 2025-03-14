# -*- coding: utf-8 -*-
# @Time    : 2023/5/26
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : ccc.py
# @Software: PyCharm
import socket
import time
from zeroconf import ServiceInfo, Zeroconf

# 服务提供者
def register_service():
    service_info = ServiceInfo(
        "_http._tcp.local.",
        "MyService._http._tcp.local.",
        addresses=[socket.inet_aton("127.0.0.1")],
        port=8080,
        properties={"version": "1.0.0"},
        server="my_service.local.",
    )

    zeroconf = Zeroconf()
    zeroconf.register_service(service_info)
    print(f"Registered {service_info.name}")

    try:
        while True:
            time.sleep(1)
    finally:
        zeroconf.unregister_service(service_info)
        zeroconf.close()


# 服务发现者
def discover_service():
    zeroconf = Zeroconf()

    def on_service_state_change(*args):
        pass

    try:
        info = zeroconf.get_service_info("_http._tcp.local.", "MyService._http._tcp.local.")
        if info:
            print("Service discovered:")
            print(f"Name: {info.name}")
            print(f"Type: {info.type}")
            print(f"Server: {info.server}")
            print(f"Addresses: {', '.join(socket.inet_ntoa(addr) for addr in info.addresses)}")
            print(f"Port: {info.port}")
            print(f"Properties: {info.properties}")
        else:
            print("Service not found")
    finally:
        zeroconf.close()


if __name__ == "__main__":
    import threading

    # 启动服务提供者和发现者线程
    provider_thread = threading.Thread(target=register_service, daemon=True)
    discoverer_thread = threading.Thread(target=discover_service, daemon=True)

    provider_thread.start()
    time.sleep(1)  # 给服务提供者一点时间注册服务
    discoverer_thread.start()

    provider_thread.join()
    discoverer_thread.join()
