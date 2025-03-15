# -*- coding: utf-8 -*-
# @Time    : 2023/2/16
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : Mysuper.py
# @Software: PyCharm
import requests


def mysuper():
    # https://content-api.mytvsuper.com/v1/channel/list?platform=web # 获取频道列表
    # https://www.mytvsuper.com/getInfo/channel/J?platform=web # 获取频道列表
    # https://content-api.mytvsuper.com/static/chunks/pages/getInfo/channel/J-ecbb64156c100f72.js # 获取频道列表
    url = "https://user-api.mytvsuper.com/v1/channel/checkout?platform=mobile_web&network_code=J&ts=1676509618018"
    # platform=mobile_web\App\web
    # phone
    # https://wv.drm.tvb.com/wvproxy/dvserial?contentid=82
    # https://wv.drm.tvb.com/wvproxy/dvserial?contentid=test
    headers = {
        "Host": "user-api.mytvsuper.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.mytvsuper.com/",
        "Authorization": "",
        "Origin": "https://www.mytvsuper.com",
        "Connection": "keep-alive",
    }
    with requests.get(url=url, headers=headers) as res:
        print(res.text)
        print(res.status_code)


def myvideo():
    url = "https://www.myvideo.net.tw/ajax/ajaxSwitchChannel.do?channelId=ch09&_=1676515398935"
    # https://www.myvideo.net.tw/ajax/ajaxFindChannelGroupList.do?_=1676516105826 # 获取频道列表
    headers = {
        "Host": "www.myvideo.net.tw",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.myvideo.net.tw/LiveChannel/",
        "Cookie": "JSESSIONID=",
    }
    with requests.get(url=url, headers=headers) as res:
        print(res.text)
        print(res.status_code)

    # ch09
    # ch15

    # # variants
    # #EXT-X-STREAM-INF:BANDWIDTH=1271000,AVERAGE-BANDWIDTH=1156000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=640x360,FRAME-RATE=29.97,VIDEO-RANGE=SDR
    # tvN-audio_140034_chi=140000-video=950000.m3u8
    # #EXT-X-STREAM-INF:BANDWIDTH=2181000,AVERAGE-BANDWIDTH=1983000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=854x480,FRAME-RATE=29.97,VIDEO-RANGE=SDR
    # tvN-audio_140034_chi=140000-video=1730000.m3u8
    # #EXT-X-STREAM-INF:BANDWIDTH=4361000,AVERAGE-BANDWIDTH=3965000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=1280x720,FRAME-RATE=29.97,VIDEO-RANGE=SDR
    # tvN-audio_140034_chi=140000-video=3600000.m3u8
    # ch12 https://news2strm.myvideo.net.tw/bpk-tv/tvN/HLS/index.m3u8

    # #EXT-X-STREAM-INF:BANDWIDTH=1083000,AVERAGE-BANDWIDTH=984000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=640x360,FRAME-RATE=30
    # MOMOTV_OTT-audio_132302_und=128000-video=800000.m3u8
    # #EXT-X-STREAM-INF:BANDWIDTH=1899000,AVERAGE-BANDWIDTH=1726000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=854x480,FRAME-RATE=30
    # MOMOTV_OTT-audio_132302_und=128000-video=1500000.m3u8
    # #EXT-X-STREAM-INF:BANDWIDTH=3881000,AVERAGE-BANDWIDTH=3528000,CODECS="mp4a.40.2,avc1.640029",RESOLUTION=1280x720,FRAME-RATE=30
    # MOMOTV_OTT-audio_132302_und=128000-video=3200000.m3u8
    # #EXT-X-STREAM-INF:BANDWIDTH=4581000,AVERAGE-BANDWIDTH=4164000,CODECS="mp4a.40.2,avc1.64002A",RESOLUTION=1920x1080,FRAME-RATE=30
    # MOMOTV_OTT-audio_132302_und=128000-video=3800000.m3u8
    # ch04 https://news2strm.myvideo.net.tw/bpk-tv/MOMOTV_OTT/HLS/index.m3u8

    # #EXT-X-STREAM-INF:BANDWIDTH=1248000,AVERAGE-BANDWIDTH=1135000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=640x360,FRAME-RATE=29.97,VIDEO-RANGE=SDR
    # CBeebies-audio_120034_chi=120000-video=950000.m3u8
    # #EXT-X-STREAM-INF:BANDWIDTH=2146000,AVERAGE-BANDWIDTH=1951000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=854x480,FRAME-RATE=29.97,VIDEO-RANGE=SDR
    # CBeebies-audio_120034_chi=120000-video=1720000.m3u8
    # #EXT-X-STREAM-INF:BANDWIDTH=4338000,AVERAGE-BANDWIDTH=3944000,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=1280x720,FRAME-RATE=29.97,VIDEO-RANGE=SDR
    # CBeebies-audio_120034_chi=120000-video=3600000.m3u8
    # ch11 https://news2strm.myvideo.net.tw/bpk-tv/CBeebies/HLS/index.m3u8

def hamivideo():
    pass

def elta():
    # https://piceltaott-elta.cdn.hinet.net/production/json/vod/vod_recommend_v2.json
    url = "https://www.elta.gr/elta-tv"
    #     https://eltaottweblive-cds.cdn.hinet.net/out/u/live/gop2/cht/hamitv-live62/hls-ae-tv/index.m3u8?token=ulkz-ByIXMNbxsEEO6pX0g&expires=1676531749&ott_id=1408727

if __name__ == '__main__':
    # mysuper()
    myvideo()