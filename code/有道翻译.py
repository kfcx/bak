# -*- coding: utf-8 -*-
# @Time    : 2023/4/14
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : 有道翻译.py
# @Software: PyCharm
import requests
import hashlib
import base64
import time
import json
from Crypto.Cipher import AES
from Crypto.Hash import MD5


class YouDao:
    def __init__(self):
        self.l = "fanyideskweb"
        self.d = "webfanyi"
        self.AES_KEY = b"ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
        self.AES_IV = b"ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
        self.const_secret_key = "asdjnjfenknafdfsdfsd"
        self.sessionObj = requests.session()

    def encrypt_md5(self, str):
        md = hashlib.md5(str.encode('utf-8')).hexdigest()
        return md

    def set_cookie_request(self):
        t = int(time.time() * 1000)
        # var g = new Date(b.lastModified); E = g.getTime() / 1e3; // b =
        # document
        last_modified = (t - 14 * 86400000) // 1000
        url = f"https://rlogs.youdao.com/rlog.php?_npid=fanyiweb&_ncat=pageview&_ncoo=775934043.5983925&_nssn=NULL&_nver=1.2.0&_ntms={t}&_nref=http%3A%2F%2Ffanyi.youdao.com%2F&_nurl=https%3A%2F%2Ffanyi.youdao.com%2Findex.html%23%2F&_nres=1440x900&_nlmf={last_modified}&_njve=0&_nchr=utf-8&_nfrg=%2F&/=NULL&screen=1440*900"
        resp = self.sessionObj.get(url)
        print('https://rlogs.youdao.com/rlog.php headers', resp.headers)  # dbg
        print('self.sessionObj.cookies',
              self.sessionObj.cookies.items())  # dbg

    def prepare_secret_key_params(self):
        t = str(int(time.time() * 1000))
        sign = self.get_sign(t, self.const_secret_key)
        params = {
            "sign": sign,
            "client": "fanyideskweb",
            "product": "webfanyi",
            "appVersion": "1.0.0",
            "vendor": "web",
            "pointParam": "client,mysticTime,product",
            "mysticTime": t,
            "keyfrom": "fanyi.web",
            "keyid": "webfanyi-key-getter",
        }
        return params

    def get_secret_key(self):
        params = self.prepare_secret_key_params()
        secret_key_url = "https://dict.youdao.com/webtranslate/key"
        res = self.sessionObj.get(secret_key_url, params=params).json()
        secret_key = res["data"]["secretKey"]
        print(secret_key)  # dbg
        return secret_key

    def get_sign(self, t, key):
        sign = self.encrypt_md5(
            f"client={self.l}&mysticTime={t}&product={self.d}&key={key}")
        return sign

    def youdao_decrypt(self, src: str) -> dict:
        key = self.AES_KEY
        iv = self.AES_IV
        cryptor = AES.new(
            MD5.new(key).digest()[:16],
            AES.MODE_CBC,
            MD5.new(iv).digest()[:16]
        )
        res = cryptor.decrypt(base64.urlsafe_b64decode(src))
        txt = res.decode("utf-8")
        return json.loads(txt[:txt.rindex("}") + 1])

    def get_actual_translate_result(self, resultJSON):
        result = ''
        for arr in resultJSON["translateResult"]:
            for item in arr:
                result += item["tgt"]
        return result

    def prepare_translate_data(self, msg, secret_key):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://fanyi.youdao.com",
            "Referer": "https://fanyi.youdao.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\""}
        t = str(int(time.time() * 1000))
        sign = self.get_sign(t, secret_key)
        data = {
            "i": f"{msg}",
            "from": "auto",
            "to": "",
            "dictResult": "true",
            "keyid": "webfanyi",
            "sign": f"{sign}",
            "client": "fanyideskweb",
            "product": "webfanyi",
            "appVersion": "1.0.0",
            "vendor": "web",
            "pointParam": "client,mysticTime,product",
            "mysticTime": f"{t}",
            "keyfrom": "fanyi.web"
        }
        return headers, data

    def translate(self, msg):
        self.set_cookie_request()
        secret_key = self.get_secret_key()
        headers, data = self.prepare_translate_data(msg, secret_key)
        translate_url = "https://dict.youdao.com/webtranslate"
        response = self.sessionObj.post(
            translate_url, headers=headers, data=data).text
        print(response)  # dbg
        resultJSON = self.youdao_decrypt(response)
        print(resultJSON)  # dbg
        result = self.get_actual_translate_result(resultJSON)
        return resultJSON, result


if __name__ == '__main__':
    youDao = YouDao()
    msg = input("输入内容：")
    if msg:
        resultJSON, result = youDao.translate(msg)
        print(result)
    else:
        print("输入为空")
