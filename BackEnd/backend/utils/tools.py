#!/usr/bin python3
# -*- coding: utf-8 -*-
import re
import time
import hashlib
from urllib.parse import urlencode, unquote, urlparse, parse_qsl, urlunparse

from backend.config import settings


def hash_url(url: str) -> str:
    """
    生成url的hash值
    :param url: url
    :return: hash值
    """
    return hashlib.md5(url.encode()).hexdigest()[8:-8]


def safe_int(s):
    try:
        return int(s)
    except ValueError:
        return s


def now_time(_=None):
    if _:
        return time.time()
    else:
        return int(time.time())


def md5(s, _=16):
    m = hashlib.md5(str(s).encode("utf-8"))
    if _ == 16:  # 16
        return m.hexdigest()[8:-8]
    else:  # 32
        return m.hexdigest()


def is_url(url):
    regex = re.compile(settings.url_regex)
    if regex.match(url):
        return True
    else:
        return False


def parse(url):
    url = urlencode(url).replace("url=", "")
    url = unquote(url)
    return url


def splicing(url, query_params):
    url_parsed = list(urlparse(url))
    temp_para = parse_qsl(url_parsed[4])
    temp_para.extend(parse_qsl(query_params.__str__()))
    url_parsed[4] = urlencode(temp_para)
    url_new = urlunparse(url_parsed)
    return url_new

