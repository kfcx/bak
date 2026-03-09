import json
import binascii
import time
from arc4 import ARC4
from Crypto.Cipher import DES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms


def pkcs7_padding(data):
    if not isinstance(data, bytes):
        data = data.encode()
    padder = padding.PKCS7(algorithms.AES.block_size // 2).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


# 加密数据
def 数据加密(data: str, key: str, mode):
    result = ""
    key = (key.encode("utf-8"))
    if mode == 1:
        en = DES.new(key, DES.MODE_ECB)
        data = pkcs7_padding(data.encode('utf-8'))
        result = str(binascii.b2a_hex(en.encrypt(data)), "utf-8")
    elif mode == 3:
        arc4 = ARC4(key)
        result = str(binascii.b2a_hex(arc4.encrypt(data.encode())), "utf-8")
    return result


# 解密数据
def 数据解密(data: str, key: str, mode):
    result = ""
    key = (key.encode("utf-8"))
    if mode == 1:
        de = DES.new(key, DES.MODE_ECB)
        b = binascii.a2b_hex(data.encode("utf-8"))
        decrypted_text = str(de.decrypt(b), 'utf-8').replace('\0', '') \
            .replace('\x01', '').replace('\x02', '').replace('\x03', '') \
            .replace('\x04', '').replace('\x05', '').replace('\x06', '') \
            .replace('\x07', '').replace('\x08', '').replace('\x09', '') \
            .replace('\x0a', '').replace('\x0b', '').replace('\x0c', '') \
            .replace('\x0d', '').replace('\x0e', '').replace('\x0f', '').replace('\x10', '')
        return decrypted_text
    elif mode == 3:
        arc4 = ARC4(key)
        # b = binascii.a2b_hex(data.encode("utf-8"))
        b = binascii.a2b_hex(data.encode("gbk"))
        result = arc4.decrypt(b)
    return result


# appid = "43917"
请求通讯key = 'zy.'  # 多功能
响应通讯key = '932476'  # 多功能
加密类型 = 3  # 1=DES 3=RC4
def main():
    # a = 数据加密(str(data), 请求通讯key, 加密类型)
    # print(a)
    a = 数据解密(data, 请求通讯key, 加密类型)
    print(a)


if __name__ == '__main__':
    main()
