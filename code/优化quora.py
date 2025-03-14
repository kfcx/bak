# -*- coding: utf-8 -*-
# @Time    : 2023/3/25
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : 优化quora.py
# @Software: PyCharm
import json
import logging
import re
import requests
import time
from requests.adapters import HTTPAdapter


class QuoraBot():
    def __init__(self, conf: dict):
        self.url = 'https://www.quora.com/poe_api/gql_POST'
        self.headers = {
            'Host': 'www.quora.com',
            'Accept': '*/*',
            'apollographql-client-version': '1.1.6-65',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Poe 1.1.6 rv:65 env:prod (iPhone14,2; iOS 16.2; en_US)',
            'apollographql-client-name': 'com.quora.app.Experts-apollo-ios',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Quora-Formkey': conf.get('formkey') or self.getFormkey(),
            'Cookie': conf.get('Cookie'),
        }
        self.request = requests.session()
        self.request.mount('https://', HTTPAdapter(max_retries=3))
        self.bot = conf.get('llm', 'capybara')
        self.chat_id = self.load_chat_id_map()
        self.clear_context()
        self.state = None

    def getFormkey(self):
        pattern = r'formkey": "(.*?)", "errorSamplingRate'
        match = re.search(pattern, requests.get('https://www.quora.com', headers=self.headers).text)
        if match:
            return match.group(1)

    def load_chat_id_map(self):
        # data = {
        #     "a2": 4049843,
        #     "capybara": 4050637,
        #     "nutria": 4173959,
        #     "a2_2": 4053326,
        #     "beaver": 4058561,
        # }
        # return data.get(self.bot)
        data = {
            'operationName': 'ChatViewQuery',
            'query': 'query ChatViewQuery($bot: String!) {\n  chatOfBot(bot: $bot) {\n    __typename\n    ...ChatFragment\n  }\n}\nfragment ChatFragment on Chat {\n  __typename\n  id\n  chatId\n  defaultBotNickname\n  shouldShowDisclaimer\n}',
            'variables': {
                'bot': self.bot
            }
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()['data']['chatOfBot']['chatId']

    def send_message(self, message):
        if self.state == "incomplete":
            return
        data = {
            "operationName": "AddHumanMessageMutation",
            "query": "mutation AddHumanMessageMutation($chatId: BigInt!, $bot: String!, $query: String!, $source: MessageSource, $withChatBreak: Boolean! = false) {\n  messageCreate(\n    chatId: $chatId\n    bot: $bot\n    query: $query\n    source: $source\n    withChatBreak: $withChatBreak\n  ) {\n    __typename\n    message {\n      __typename\n      ...MessageFragment\n      chat {\n        __typename\n        id\n        shouldShowDisclaimer\n      }\n    }\n    chatBreak {\n      __typename\n      ...MessageFragment\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n  suggestedReplies\n}",
            "variables": {
                "bot": self.bot,
                "chatId": self.chat_id,
                "query": message,
                "source": None,
                "withChatBreak": False
            }
        }
        _rspn = self.request.post(url=self.url, headers=self.headers, json=data)
        if _rspn.json()["data"]:
            self.state = "incomplete"
            return self.get_latest_message()
        else:
            return "今日次数用完"

    def clear_context(self):
        data = {
            "operationName": "AddMessageBreakMutation",
            "query": "mutation AddMessageBreakMutation($chatId: BigInt!) {\n  messageBreakCreate(chatId: $chatId) {\n    __typename\n    message {\n      __typename\n      ...MessageFragment\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n  suggestedReplies\n}",
            "variables": {
                "chatId": self.chat_id
            }
        }
        _rspn = self.request.post(url=self.url, headers=self.headers, json=data)

    def get_latest_message(self):
        data = {
            "operationName": "ChatPaginationQuery",
            "query": "query ChatPaginationQuery($bot: String!, $before: String, $last: Int! = 10) {\n  chatOfBot(bot: $bot) {\n    id\n    __typename\n    messagesConnection(before: $before, last: $last) {\n      __typename\n      pageInfo {\n        __typename\n        hasPreviousPage\n      }\n      edges {\n        __typename\n        node {\n          __typename\n          ...MessageFragment\n        }\n      }\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n}",
            "variables": {
                "before": None,
                "bot": self.bot,
                "last": 1
            }
        }
        replyText = None
        while self.state == "incomplete":
            time.sleep(2)
            _rspn = self.request.post(url=self.url, headers=self.headers, json=data)
            response_json = _rspn.json()['data']['chatOfBot']['messagesConnection']['edges'][-1]['node']
            logging.getLogger('itchat').info(response_json)
            replyText = response_json['text']
            self.state = response_json['state']
            if self.state == "complete":
                return replyText
            logging.getLogger('itchat').debug(self.state)
        return replyText

    def reply(self, message: str, context=None):
        replyText = self.send_message(message)
        if context is not None:
            with open('./user_session.json', 'w', encoding='utf-8') as f:
                json.dump(context, f)
        return replyText


def main():
    conf = {
        "llm": "a2",
        "Cookie": "m-b=_9Cg==",
        "formkey": ""
    }
    # ---------------------------------------------------------------------------
    print("Who do you want to talk to?")
    print("1. Claude - Anthropic (a2)")
    print("2. ChatGPT-Big - OpenAI (capybara)")
    print("3. ChatGPT-Small - Openai (nutria)")
    # ---------------------------------------------------------------------------
    option = input("Please enter your choice : ")
    bots = {1: 'a2', 2: 'capybara', 3: 'nutria', 4: 'a2_2', 5: 'beaver'}
    # 1：4049843  2：4050637  3：4173959  4：4053326  5：4058561
    conf["llm"] = bots[int(option)]
    print("The selected bot is : ", bots[int(option)])
    # ---------------------------------------------------------------------------
    poe = QuoraBot(conf)
    print("Context is now cleared")
    while True:
        message = input("Human : ")
        if message == "!clear":
            poe.clear_context()
            print("Context is now cleared")
            continue
        if message == "!break":
            break
        print(poe.reply(message))


if __name__ == '__main__':
    main()
    
