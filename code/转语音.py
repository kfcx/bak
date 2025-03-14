# -*- coding: utf-8 -*-
# @Time    : 2023/4/5
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : 转语音.py
# @Software: PyCharm
import requests
from io import BytesIO
from loguru import logger


def synthetize(text: str, language: str) -> BytesIO:
    chunked_text = [text[i:i + 200] for i in range(0, len(text), 200)]
    streams = []

    for chunk in chunked_text:
        streams.append(synthetize_chunk(chunk, language))

    return merge(*streams)


def synthetize_chunk(text: str, language: str) -> BytesIO:
    parsed_text = requests.utils.quote(text.lower())
    logger.debug(f"Urlencoded text for google: {text} ({len(parsed_text)})")
    audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={parsed_text}&tl={language}&client=tw-ob&ttsspeed=1"
    response = requests.get(audio_url)

    return BytesIO(response.content)


def merge(*streams) -> BytesIO:
    output = BytesIO()
    for stream in streams:
        output.write(stream.read())
    output.seek(0)
    return output


def main():
    a = synthetize_chunk("你好", "zh")
    with open("hello.mp3", "wb") as f:
        f.write(a.read())


if __name__ == '__main__':
    main()
