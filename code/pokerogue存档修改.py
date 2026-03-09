import time
import json
from curl_cffi import requests


def demos():
    import execjs

    secret_key = 'x0i2O7WRiANTqPmZ'
    node = execjs.get()
    ctx = node.compile(open('aes.js', 'r', encoding='utf-8').read())
    # encrypt_rst = ctx.call('encrypt', '123456', secret_key)
    # print(encrypt_rst)
    encrypt_rst = ""
    decrypt_rst = ctx.call('decrypt', encrypt_rst, secret_key)
    print(decrypt_rst)


def getParam():
    starterData = {}
    dexData = {}
    for i in range(1, 1025 + 1):  # Unlock shiny6v
        starterData[str(i)] = {
            "abilityAttr": 7,
            "candyCount": 200,
            "eggMoves": 15,
            "friendship": 90,
            "passiveAttr": 3,
            "valueReduction": 2
        }
        dexData[str(i)] = {
            "caughtAttr": 255,
            "ivs": [31, 31, 31, 31, 31, 31],
            "seenAttr": 479,
            "caughtcount": 3,
            "hatchedCount": 3,
            "seenCount": 3,
            "natureAttr": 67108862
        }

    targetIndices = [
        2019, 2020, 2026, 2027, 2028, 2037, 2038, 2050, 2051, 2052, 2053,
        2074, 2075, 2076, 2088, 2089, 2103, 2105, 2670, 4052, 4077,
        4078, 4079, 4080, 4083, 4110, 4122, 4144, 4145, 4146, 4199,
        4222, 4263, 4264, 4554, 4555, 4562, 4618, 6058, 6059, 6100,
        6101, 6157, 6211, 6215, 6503, 6549, 6570, 6571, 6628, 6705,
        6706, 6713, 6724, 8128, 8194, 8901
    ]
    for i in targetIndices:
        starterData[str(i)] = {
            "abilityAttr": 7,
            "candyCount": 200,
            "eggMoves": 15,
            "friendship": 90,
            "passiveAttr": 3,
            "valueReduction": 2
        }
        dexData[str(i)] = {
            "caughtAttr": 255,
            "ivs": [31, 31, 31, 31, 31, 31],
            "seenAttr": 479,
            "caughtCount": 3,
            "hatchedCount": 3,
            "seenCount": 3,
            "natureAttr": 67108862
        }

    excludeIndices = [25, 35, 39, 106, 107, 113, 122, 124, 125, 126, 143, 183, 185, 202, 226, 315, 358, 412]
    for i in range(1, 1025 + 1):  # Fix pikachu etc
        if excludeIndices.count(i):
            continue
        starterData[str(i)] = {
            "abilityAttr": 7,
            "candyCount": 200,
            "eggMoves": 15,
            "friendship": 90,
            "passiveAttr": 3,
            "valueReduction": 2
        }
        dexData[str(i)] = {
            "caughtAttr": 255,
            "ivs": [31, 31, 31, 31, 31, 31],
            "seenAttr": 479,
            "caughtcount": 3,
            "hatchedCount": 3,
            "seenCount": 3,
            "natureAttr": 67108862
        }

    targetIndices = [
        2019, 2020, 2026, 2027, 2028, 2037, 2038, 2050, 2051, 2052, 2053,
        2074, 2075, 2076, 2088, 2089, 2103, 2105, 2670, 4052, 4077,
        4078, 4079, 4080, 4083, 4110, 4144, 4145, 4146, 4199,
        4222, 4263, 4264, 4554, 4555, 4562, 4618, 6058, 6059, 6100,
        6101, 6157, 6211, 6215, 6503, 6549, 6570, 6571, 6628, 6705,
        6706, 6713, 6724, 8128, 8194, 8901
    ]
    for i in targetIndices:
        starterData[str(i)] = {
            "abilityAttr": 7,
            "candyCount": 200,
            "eggMoves": 15,
            "friendship": 90,
            "passiveAttr": 3,
            "valueReduction": 2
        }
        dexData[str(i)] = {
            "caughtAttr": 255,
            "ivs": [31, 31, 31, 31, 31, 31],
            "seenAttr": 479,
            "caughtcount": 3,
            "hatchedCount": 3,
            "seenCount": 3,
            "natureAttr": 67108862
        }

    targetIndices1 = [25, 35, 39, 106, 107, 113, 122, 124, 125, 126, 143, 183, 185, 202, 226, 315, 358, 412]
    for i in range(1, 1025 + 1):
        if targetIndices1.count(i):
            continue
        starterData[str(i)] = {
            "abilityAttr": 7,
            "candyCount": 200,
            "eggMoves": 15,
            "friendship": 90,
            "passiveAttr": 0,
            "valueReduction": 2
        }
        dexData[str(i)] = {
            "caughtAttr": 255,
            "ivs": [31, 31, 31, 31, 31, 31],
            "seenAttr": 479,
            "caughtcount": 3,
            "hatchedCount": 3,
            "seenCount": 3,
            "natureAttr": 67108862
        }

    targetIndices2 = [
        4122
    ]
    for i in targetIndices2:
        starterData[str(i)] = {
            "abilityAttr": 7,
            "candyCount": 200,
            "eggMoves": 15,
            "friendship": 90,
            "passiveAttr": 0,
            "valueReduction": 2
        }
        dexData[str(i)] = {
            "caughtAttr": 255,
            "ivs": [31, 31, 31, 31, 31, 31],
            "seenAttr": 479,
            "caughtcount": 3,
            "hatchedCount": 3,
            "seenCount": 3,
            "natureAttr": 67108862
        }

    noGender = [
        81, 100, 120, 132, 137, 144, 145, 146, 150, 151,
        243, 244, 245, 249, 250, 251,
        337, 338, 343, 374, 377, 378, 379, 382, 383, 384, 385, 386,
        436, 479, 480, 481, 482, 483, 484, 486, 487, 489, 490, 491, 492, 493, 494,
        599, 615, 622, 638, 639, 640, 643, 644, 646, 647, 648, 649,
        703, 716, 717, 718, 719, 720,
        721, 772, 774, 781, 785, 786, 787, 788, 789, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 805, 806, 807,
        808,
        854, 870, 880, 881, 882, 883, 888, 889, 890, 893, 894, 895, 896, 897, 898,
        924, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 999, 1001, 1002, 1003, 1004, 1005, 1006, 1007,
        1008, 1009, 1010, 1012, 1020, 1021, 1022, 1023, 1025,
        4144, 4145, 4146, 6100
    ]  # 无性别
    for i in noGender:  # Fix Gender
        dexData[str(i)]["caughtAttr"] = 247
    male = [
        32, 106, 107, 128, 236, 314, 381, 538, 539, 627, 641, 642, 645, 859, 1014, 1015, 1016, 8128
    ]  # 公
    for i in noGender:
        dexData[str(i)]["caughtAttr"] = 247
    female = [
        25, 29, 113, 115, 124, 238, 241, 314, 380, 440, 488, 548, 629, 669, 2670, 761, 856, 868, 905, 957, 1017
    ]  # 母
    for i in noGender:
        dexData[str(i)]["caughtAttr"] = 251

    # Unlock Forms
    dexData["656"]["caughtAttr"] = 511  # 甲贺忍蛙
    dexData["550"]["caughtAttr"] = 1023  # 野蛮鲈鱼
    dexData["25"]["caughtAttr"] = 65535  # 皮卡丘
    dexData["201"]["caughtAttr"] = 34359738367  # 未知图腾
    dexData["664"]["caughtAttr"] = 134217727  # 粉蝶虫
    dexData["8128"]["caughtAttr"] = 10115  # 帕迪亚肯泰罗
    dexData["479"]["caughtAttr"] = 8183  # 洛托姆
    dexData["585"]["caughtAttr"] = 2047  # 四季鹿
    dexData["669"]["caughtAttr"] = 4091  # 花蓓蓓
    dexData["741"]["caughtAttr"] = 2047  # 花舞鸟
    dexData["676"]["caughtAttr"] = 262143  # 多丽米亚
    dexData["978"]["caughtAttr"] = 1023  # 米粒龙
    dexData["710"]["caughtAttr"] = 2043  # 南瓜精
    dexData["848"]["caughtAttr"] = 511  # 毒电婴
    dexData["854"]["caughtAttr"] = 511  # 来悲茶
    dexData["931"]["caughtAttr"] = 2047  # 怒鹦哥
    dexData["422"]["caughtAttr"] = 503  # 无壳海兔
    dexData["999"]["caughtAttr"] = 503  # 索财灵
    dexData["801"]["caughtAttr"] = 503  # 玛机雅娜
    dexData["412"]["caughtAttr"] = 1023  # 结草儿

    targetIndices = [
        718
    ]  # Zygarde
    for i in targetIndices:
        starterData[str(i)] = {
            "abilityAttr": 1,
            "candyCount": 200,
            "eggMoves": 15,
            "friendship": 90,
            "passiveAttr": 3,
            "valueReduction": 2
        }  # ability: 特性1,4,7; eggmove:蛋招式1,4,7,15;passive:被动;
        dexData[str(i)] = {
            "caughtAttr": 2039,
            "ivs": [31, 31, 31, 31, 31, 31],
            "seenAttr": 479,
            "caughtcount": 3,
            "hatchedCount": 3,
            "seenCount": 3,
            "natureAttr": 67108862
        }

    # print(dexData)
    # print(starterData)
    return {"dexData": dexData, "starterData": starterData}


class Demo:
    def __init__(self, clientSessionId, Authorization):
        self.timestamp = int(time.time() * 1000)
        self.clientSessionId = clientSessionId
        self.Authorization = Authorization
        self.data = None

    def login(self):
        url = "https://api.pokerogue.net/account/login"
        data = {
            "username": "",
            "password": ""
        }
        headers = {
            'Host': 'api.pokerogue.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept': 'application/x-www-form-urlencoded',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://pokerogue.net/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://pokerogue.net',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
        }
        resp = requests.post(url=url, headers=headers, params=data)
        print(resp.status_code, resp.text)

    def modify_Session(self, session):
        modifiers = session["modifiers"] if session["modifiers"] else []

        param = {
            "GOLDEN_POKEBALL": {
                "args": None,
                "className": "ExtraModifierModifier",
                "player": True,
                "stackCount": 3,
                "typeId": "GOLDEN_POKEBALL"  # 黄金精灵球
            },
            # "MAP": {
            #     "args": None,
            #     "className": "MapModifier",
            #     "player": True,
            #     "stackCount": 1,
            #     "typeId": "MAP"  # 地图
            # },
            "AMULET_COIN": {
                "args": None,
                "className": "MoneyMultiplierModifier",
                "player": True,
                "stackCount": 5,
                "typeId": "AMULET_COIN"  # 护身金币
            },
            "LOCK_CAPSULE": {
                "args": None,
                "className": "LockModifierTiersModifier",
                "player": True,
                "stackCount": 1,
                "typeId": "LOCK_CAPSULE"  # 锁定胶囊
            },
            "CANDY_JAR": {
                "args": None,
                "className": "LevelIncrementBoosterModifier",
                "player": True,
                "stackCount": 99,
                "typeId": "CANDY_JAR"  # 糖果罐
            },"EXP_SHARE": {
                "args": None,
                "className": "ExpShareModifier",
                "player": True,
                "stackCount": 5,
                "typeId": "EXP_SHARE"   # 学习装置
            }, "EXP_CHARM": {
                "args": [
                    25
                ],
                "className": "ExpBoosterModifier",
                "player": True,
                "stackCount": 99,
                "typeId": "EXP_CHARM"  # 经验护符25%
            }, "SUPER_EXP_CHARM": {
                "args": [
                    60
                ],
                "className": "ExpBoosterModifier",
                "player": True,
                "stackCount": 30,
                "typeId": "SUPER_EXP_CHARM"  # 经验护符60%
            }, "SHINY_CHARM": {
                "args": None,
                "className": "ShinyRateBoosterModifier",
                "player": True,
                "stackCount": 4,
                "typeId": "SHINY_CHARM"  # 闪耀护符
            }, "ABILITY_CHARM": {
                "args": None,
                "className": "HiddenAbilityRateBoosterModifier",
                "player": True,
                "stackCount": 5,
                "typeId": "ABILITY_CHARM"  # 特性护符
            },
            # "IV_SCANNER": {
            #     "args": None,
            #     "className": "IvScannerModifier",
            #     "player": True,
            #     "stackCount": 5,
            #     "typeId": "IV_SCANNER"  # IV扫描仪
            # },
            "MEGA_BRACELET": {
                "args": None,
                "className": "MegaEvolutionAccessModifier",
                "player": True,
                "stackCount": 1,
                "typeId": "MEGA_BRACELET"  # mega手镯
            }, "DYNAMAX_BAND": {
                "args": None,
                "className": "GigantamaxAccessModifier",
                "player": True,
                "stackCount": 1,
                "typeId": "DYNAMAX_BAND"  # 极巨腕带
            }, "TERA_ORB": {
                "args": None,
                "className": "TerastallizeAccessModifier",
                "player": True,
                "stackCount": 1,
                "typeId": "TERA_ORB"  # 太晶珠
            }, "BERRY_POUCH": {
                "args": None,
                "className": "PreserveBerryModifier",
                "player": True,
                "stackCount": 3,
                "typeId": "BERRY_POUCH"  # 浆果袋
            }, "HEALING_CHARM": {
                "args": [
                    1.1
                ],
                "className": "HealingBoosterModifier",
                "player": True,
                "stackCount": 5,
                "typeId": "HEALING_CHARM"  # 治愈护身符
            }, "MAX_LURE": {
                "args": [
                    2500
                ],
                "className": "DoubleBattleChanceBoosterModifier",
                "player": True,
                "stackCount": 2555,
                "typeId": "MAX_LURE"  # 黄金香水
            },
            # "MAX_LURE2": {
            #     "args": [
            #         2502
            #     ],
            #     "className": "DoubleBattleChanceBoosterModifier",
            #     "player": True,
            #     "stackCount": 2555,
            #     "typeId": "MAX_LURE"  # 黄金香水
            # },"MAX_LURE3": {
            #     "args": [
            #         2503
            #     ],
            #     "className": "DoubleBattleChanceBoosterModifier",
            #     "player": True,
            #     "stackCount": 2555,
            #     "typeId": "MAX_LURE"  # 黄金香水
            # },"MAX_LURE4": {
            #     "args": [
            #         2504
            #     ],
            #     "className": "DoubleBattleChanceBoosterModifier",
            #     "player": True,
            #     "stackCount": 2555,
            #     "typeId": "MAX_LURE"  # 黄金香水
            # },"MAX_LURE5": {
            #     "args": [
            #         2505
            #     ],
            #     "className": "DoubleBattleChanceBoosterModifier",
            #     "player": True,
            #     "stackCount": 2555,
            #     "typeId": "MAX_LURE"  # 黄金香水
            # }
        }

        for i, v in enumerate(modifiers):
            if v.get("typeId") and v["typeId"] in param:
                modifiers[i].update(param.pop(v["typeId"]))
        if param:
            modifiers.extend(v for v in param.values())

        session["timestamp"] = self.timestamp
        session["money"] = 999999999999999999
        session["pokeballCounts"] = {k: 999 for k, v in session["pokeballCounts"].items()}
        for i, p in enumerate(session["party"]):
            session["party"][i]["shiny"] = True
            session["party"][i]["passive"] = True   # 隐藏特性
            session["party"][i]["friendship"] = 255

            session["party"][i]["stats"] = [session["party"][i]["stats"][j] + (31 - session["party"][i]["ivs"][j]) for j in
                                            range(6)]
            session["party"][i]["ivs"] = [31, 31, 31, 31, 31, 31]
            session["party"][i]["luck"] = 255
            session["party"][i]["hp"] = session["party"][i]["stats"][0]
            # data1[i]["nature"] = data1[i]["stats"][0]

        return session

    def modify_System(self, system):
        system["timestamp"] = self.timestamp
        system["voucherCounts"] = {k: 9999 for k, v in system["voucherCounts"].items()}  # 抽奖券
        system["eggs"] = system["eggs"] if system["eggs"] else []
        system["eggPity"] = [99, 99, 999, 9999]
        system["unlockPity"] = [99, 99, 99, 999]
        for i, p in enumerate(system["eggs"]):
            system["eggs"][i]["isShiny"] = True
            system["eggs"][i]["tier"] = 3  # 0普通 1稀有 2史诗 3传说
            system["eggs"][i]["hatchWaves"] = 1  # 孵化步数
            system["eggs"][i]["gachaType"] = 2  # 抽卡池 0:MOVE 1:LEGENDARY 2:SHINY
            # system["eggs"][i]["sourceType"] = 3  # GACHA_MOVE, GACHA_LEGENDARY, GACHA_SHINY, SAME_SPECIES_EGG, EVENT
            # system["eggs"][i]["VariantTier"] = 2  # COMMON:6/10, RARE:3/10, EPIC:1/10
            # system["eggs"][i]["species"] = xx  # 指定孵出某个精灵编号
            # system["eggs"][i]["eggMoveIndex"] = xx  # GACHA_MOVE, GACHA_LEGENDARY, GACHA_SHINY, SAME_SPECIES_EGG, EVENT
            # eggPity 保底设置  unlockPity  保底设置

        # for i in system["starterData"]:
        #     if system["starterData"][i]["abilityAttr"] != 0 and system["starterData"][i]["candyCount"] < 100:
        #         system["starterData"][i]["candyCount"] = 500  # 糖果数量
        #         system["starterData"][i]["friendship"] = 255  # 亲密度
        #         system["starterData"][i]["eggMoves"] = 15    # 遗传技能
        #         system["starterData"][i]["abilityAttr"] = 7    # 特性
        #         system["starterData"][i]["passiveAttr"] = 3    # 被动
        #         system["starterData"][i]["valueReduction"] = 4    # 减费 2?

        # for i in system["dexData"]:
        #     if sum(system["dexData"][i]["ivs"]) > 0:
        #         system["dexData"][i]["ivs"] = [31, 31, 31, 31, 31, 31]
        #         system["dexData"][i]["natureAttr"] = 67108862  # 性格

        return system

    def modify(self, system, session, sessionSlotId=0, offline=False):
        """

        :param sessionSlotId: 存档位置
        :return:
        """
        if offline:
            dexData = {}
            for k in [k for k in system["dexData"]]:
                dexData[k] = {
                    "seenAttr": system["dexData"][k]["$sa"],
                    "caughtAttr": system["dexData"][k]["$ca"],
                    "natureAttr": system["dexData"][k]["$na"],
                    "seenCount": system["dexData"][k]["$s"],
                    "caughtCount": system["dexData"][k]["$c"],
                    "hatchedCount": system["dexData"][k]["$hc"],
                    "ivs": system["dexData"][k]["$i"]
                }
            system["dexData"] = dexData

            starterData = {}
            for k in [k for k in system["starterData"]]:
                starterData[k] = {
                    "moveset": system["starterData"][k]["$m"],
                    "eggMoves": system["starterData"][k]["$em"],
                    "candyCount": system["starterData"][k]["$x"],
                    "friendship": system["starterData"][k]["$f"],
                    "abilityAttr": system["starterData"][k]["$a"],
                    "passiveAttr": system["starterData"][k]["$pa"],
                    "valueReduction": system["starterData"][k]["$vr"],
                    "classicWinCount": system["starterData"][k]["$wc"]
                }
            system["starterData"] = starterData

        data = {"system": None, "session": None, "sessionSlotId": sessionSlotId, "clientSessionId": self.clientSessionId}
        # data["session"] = self.modify_Session(session)
        data["session"] = session
        # data["system"] = self.modify_System(system)
        data["system"] = system

        self.data = data

    def updateall(self):
        url = "https://api.pokerogue.net/savedata/updateall"
        headers = {
            'Host': 'api.pokerogue.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://pokerogue.net/',
            'Content-Type': 'application/json',
            'Authorization': self.Authorization,
            'Origin': 'https://pokerogue.net',
            'Connection': 'keep-alive'
        }
        if self.data is None:
            raise Exception("无发送数据")
        resp = requests.post(url=url, headers=headers, json=self.data)
        print(resp.status_code)
        print(resp.text)

    def updateSystem(self):
        url = f"https://api.pokerogue.net/savedata/system/update?clientSessionId={self.clientSessionId}"
        headers = {
            'Host': 'api.pokerogue.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://pokerogue.net/',
            'Content-Type': 'application/json',
            'Authorization': self.Authorization,
            'Origin': 'https://pokerogue.net',
            'Connection': 'keep-alive'
        }
        if self.data is None:
            raise Exception("无发送数据")
        data = self.data["system"]
        data.pop("starterMoveData"), data.pop("starterEggMoveData")
        resp = requests.post(url=url, headers=headers, json=data)
        print(resp.status_code)
        print(resp.text)

    def get_SystemData(self):
        url = f"https://api.pokerogue.net/savedata/system/get?clientSessionId={self.clientSessionId}"
        headers = {
            'Host': 'api.pokerogue.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://pokerogue.net/',
            'Authorization': self.Authorization,
            'Origin': 'https://pokerogue.net',
            'Connection': 'keep-alive'
        }
        resp = requests.get(url=url, headers=headers)
        print(resp.status_code)
        print(resp.text)
        return resp.json()

    def get_SessionData(self, slot=0):
        """

        :param slot: 存档位置
        :return:
        """
        url = f"https://api.pokerogue.net/savedata/session/get?slot={slot}&clientSessionId={self.clientSessionId}"
        # url = f"https://api.pokerogue.net/savedata/session/get?slot=2&clientSessionId={clientSessionId}"
        headers = {
            'Host': 'api.pokerogue.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://pokerogue.net/',
            'Authorization': self.Authorization,
            'Origin': 'https://pokerogue.net',
            'Connection': 'keep-alive'
        }
        resp = requests.get(url=url, headers=headers)
        print(resp.status_code)
        print(resp.text)
        return resp.json()


def main():
    clientSessionId = ""
    Authorization = "="
    demo = Demo(clientSessionId, Authorization)

    slot = 0  # 存档位置
    offline = False

    session = json.loads(session)
    system = json.loads(system)
    party = json.loads(party)
    session["party"] = party["party"]

    # system = demo.get_SystemData()
    # session = demo.get_SessionData(slot)

    # t = time.localtime(time.time())
    # with open(f"demo/system={t.tm_year}.{t.tm_mon}.{t.tm_mday} {t.tm_hour}_{t.tm_min}_{t.tm_sec}", "w") as fp:
    #     fp.write(json.dumps(system))
    # with open(f"demo/session={t.tm_year}.{t.tm_mon}.{t.tm_mday} {t.tm_hour}_{t.tm_min}_{t.tm_sec}", "w") as fp:
    #     fp.write(json.dumps(session))
    demo.modify(system, session, slot, offline)
    demo.updateall()

    # data = getParam()     # 修改全闪蛋
    # system.update(data)
    # demo.modify(system, session, slot, offline)
    # demo.updateSystem()


if __name__ == '__main__':
    main()
    demos()


# gender -1：无性别  0：公  1：母
# gameMode: 4挑战模式
# waveIndex # 通关关卡
# score
# money
# timestamp
# arena.biome
# gameStats.playTime
# gameStats.battles
# gameStats.pokemonSeen
# gameStats.pokemonDefeated
# gameStats.battles
# session.enemyParty    # 对手
# pokeballCounts   # 精灵球
# voucherCounts     # 蛋
# nature 性格 3固执
# pokerus 病毒

    # 掀榻榻米
    # 烧净
    # 怒火中烧
    # 核心惩罚者
    # 钻石风暴
    # 断崖之剑
    # 雷电囚笼
    # 巨龙威能
    # 星碎
    # 雪矛
    # 龙尾
    # 捕兽夹
    # 自然之怒
    # 大灾难
    # 愤怒门牙
    # 钢拳双击
    # 寄生种子
    # 茁茁炸弹
    # 麻麻刺刺
    # 三连箭
    # 盐腌
    # 种子闪光
    # v热焰
    # 雷击

    # 陆地水母 先手蘑菇孢子
    # 一般幽灵脱壳 逃跑 寄生
    # 畏缩 巨石丁+Giga灰尘山

    # 幽灵马王898紧张感  822 548 825 561
    # 陆地水母+结实恶心随眠 949 147 18 575 561
    # 直冲熊264+脱壳 292 738、487、864、717


