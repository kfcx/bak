from pydantic import BaseModel
from pymailtm import MailTm, Message
import re
import json
from typing import Optional, Union, Generator, Dict, List
import fake_useragent
import tls_client
import requests
import logging


class EmailResponse(BaseModel):
    sessionID: str
    client: str


class DeltaResponse(BaseModel):
    content: Optional[Union[str, None]] = ''


class ChoicesResponse(BaseModel):
    index: int
    finish_reason: Optional[Union[str, None]] = ''
    delta: DeltaResponse
    usage: Optional[Union[str, None]] = ''


class ForeFrontResponse(BaseModel):
    model: str
    choices: List[ChoicesResponse]


class Email:
    @classmethod
    def __init__(self: type) -> None:
        self.__SETUP_LOGGER()
        self.__session: tls_client.Session = tls_client.Session(client_identifier="chrome_108")

    @classmethod
    def __SETUP_LOGGER(self: type) -> None:
        self.__logger: logging.getLogger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter: logging.Formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        self.__logger.addHandler(console_handler)

    @classmethod
    def __AccountState(self: object, output: str, field: str) -> bool:
        if field not in output:
            return False
        return True

    @classmethod
    def CreateAccount(self: object) -> str | EmailResponse:
        mail_client = MailTm().get_account()
        mail_address = mail_client.address
        print(mail_address)

        self.__session.headers = {
            "Origin": "https://accounts.forefront.ai",
            "User-Agent": fake_useragent.UserAgent().random
        }

        self.__logger.debug("Checking URL")

        output = self.__session.post("https://clerk.forefront.ai/v1/client/sign_ups?_clerk_js_version=4.38.4",
                                     data={"email_address": mail_address})

        if not self.__AccountState(str(output.text), "id"):
            self.__logger.error("Failed to create account :(")
            return "Failed"

        trace_id = output.json()["response"]["id"]

        output = self.__session.post(
            f"https://clerk.forefront.ai/v1/client/sign_ups/{trace_id}/prepare_verification?_clerk_js_version=4.38.4",
            data={"strategy": "email_link", "redirect_url": "https://accounts.forefront.ai/sign-up/verify"})

        if not self.__AccountState(output.text, "sign_up_attempt"):
            self.__logger.error("Failed to create account :(")
            return "Failed"

        self.__logger.debug("Verifying account")

        while True:
            new_message: Message = mail_client.wait_for_message()

            verification_url = re.findall(r"https:\/\/clerk\.forefront\.ai\/v1\/verify\?token=\w.+", new_message.text)[
                0]
            if verification_url:
                break

        r = self.__session.get(verification_url)
        __client: str = r.cookies["__client"]

        output = self.__session.get("https://clerk.forefront.ai/v1/client?_clerk_js_version=4.38.4")
        token: str = output.json()["response"]["sessions"][0]["last_active_token"]["jwt"]
        print(token)
        sessionID: str = output.json()["response"]["last_active_session_id"]

        self.__logger.debug("Created account!")
        print({"sessionID": sessionID, "client": __client})

        return EmailResponse(**{"sessionID": sessionID, "client": __client})


class Model:
    @classmethod
    def __init__(self: object, sessionID: str, client: str, model: Optional[str] = "gpt-3.5-turbo",
                 persona: Optional[str] = "607e41fe-95be-497e-8e97-010a59b2e2c0",
                 conversationID: Optional[Union[str, None]] = None
                 ) -> None:
        self.__SETUP_LOGGER()
        self.__WORKSPACEID: str = ''
        self.__session: requests.Session = requests.Session()
        self.__model: str = model
        self.__SESSION_ID: str = sessionID
        self.__CONVERSATION_ID: str = conversationID
        self.__CLIENT: str = client
        self.__PERSONA: str = persona
        self.__JSON: Dict[str, str] = {}
        self.__HEADERS: Dict[str, str] = {
            "Authority": "streaming.tenant-forefront-default.knative.chi.coreweave.com",
            "Accept": "*/*",
            "Accept-Language": "en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3",
            "Authorization": f"Bearer {self.__CLIENT}",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Origin": "https://chat.forefront.ai",
            "Pragma": "no-cache",
            "Referer": "https://chat.forefront.ai/",
            "Sec-Ch-Ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "Sec-Ch-Ua-mobile": "?0",
            "Sec-Ch-Ua-platform": "\"macOS\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": fake_useragent.UserAgent().random
        }

        self.__JWT_HEADERS: Dict[str, str] = {
            "Authority": "clerk.forefront.ai",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://chat.forefront.ai",
            "Pragma": "no-cache",
            "Cookie": f"__client={self.__CLIENT}",
            "Sec-Ch-Ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "Sec-Ch-Ua-mobile": "?0",
            "Sec-Ch-Ua-platform": "\"macOS\"",
            "Referer": "https://chat.forefront.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": fake_useragent.UserAgent().random
        }

        self.__WORKSPACEID = self.__GetWorkspaceID()
        self.__logger.debug("Connected in Workspace: " + self.__WORKSPACEID)

    @classmethod
    def __SETUP_LOGGER(self: type) -> None:
        self.__logger: logging.getLogger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        self.__logger.addHandler(console_handler)

    @classmethod
    def __UpdateJWTToken(self: type) -> None:
        jwt_token: Dict[str, str] = self.__session.post(
            f"https://clerk.forefront.ai/v1/client/sessions/{self.__SESSION_ID}/tokens?_clerk_js_version=4.38.4",
            headers=self.__JWT_HEADERS).json()
        print(jwt_token)
        jwt_token = jwt_token["jwt"]
        self.__HEADERS["Authorization"] = f"Bearer {jwt_token}"

    @classmethod
    def __GetWorkspaceID(self: type) -> str:
        self.__UpdateJWTToken()
        url: str = "https://chat-api.tenant-forefront-default.knative.chi.coreweave.com/api/trpc/workspaces.listWorkspaces,chat.loadTree?batch=1&input="
        payload: str = "{\"0\":{\"json\":null,\"meta\":{\"values\":[\"undefined\"]}},\"1\":{\"json\":{\"workspaceId\":\"\"}}}"

        return self.__session.get(url + payload, headers=self.__HEADERS).json()[0]["result"]["data"]["json"][0]["id"]

    @classmethod
    def SetupConversation(self: type, prompt: str) -> None:
        self.__JSON = {
            "text": prompt,
            "action": "new",
            "parentId": self.__WORKSPACEID,
            "workspaceId": self.__WORKSPACEID,
            "messagePersona": self.__PERSONA,
            "model": self.__model
        }

    @classmethod
    def IsAccountActive(self: type) -> bool:
        return self.__session.post(
            f"https://clerk.forefront.ai/v1/client/sessions/{self.__SESSION_ID}/touch?_clerk_js_version=4.38.4",
            headers=self.__JWT_HEADERS).status_code == 200

    @classmethod
    def SendConversation(self: object) -> Generator[ForeFrontResponse, None, None]:
        token: str = ''
        __HEADERS: Dict[str, str] = {
            "Authority": "clerk.forefront.ai",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://chat.forefront.ai",
            "Pragma": "no-cache",
            "Cookie": f"__client={self.__CLIENT}",
            "Sec-Ch-Ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "Sec-Ch-Ua-mobile": "?0",
            "Sec-Ch-Ua-platform": "\"macOS\"",
            "Referer": "https://chat.forefront.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": fake_useragent.UserAgent().random
        }

        self.__UpdateJWTToken()
        for chunk in self.__session.post("https://streaming.tenant-forefront-default.knative.chi.coreweave.com/chat",
                                         headers=self.__HEADERS, json=self.__JSON, stream=True
                                         ).iter_lines():
            if b"finish_reason\":null" in chunk:
                data = json.loads(chunk.decode('utf-8').split("data: ")[1])
                yield ForeFrontResponse(**data)


def main():
    client = "eyJhbGciOiJSUzI1NiIsImtpZCI6Imluc18yTzZ3UTFYd3dxVFdXUWUyQ1VYZHZ2bnNaY2UiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwczovL2NoYXQuZm9yZWZyb250LmFpIiwiZXhwIjoxNjgzMDk0NDQ5LCJpYXQiOjE2ODMwOTQzODksImlzcyI6Imh0dHBzOi8vY2xlcmsuZm9yZWZyb250LmFpIiwibmJmIjoxNjgzMDk0Mzc5LCJzaWQiOiJzZXNzXzJQR3BmVFFWRmV2dm5vOUs0UEhRMUtZbTN1QiIsInN1YiI6InVzZXJfMlBHcGZUZVo3UWNaeDBpYkx0R2NnaEoxMUpmIn0.b7U7alPi_AoNQlSkznfy46h7J9DifNLZlbgpIRmd0LA_uPBSsQ31wS5YoAsCydIdKR_bE-f-fro4U4-V8kleKAy6L9efL8jGuulx9GDFTLoGwMAVukb-7W_8aKuHgattcnHFYTCGvvxKvJMo1t5SPKaJ4N9fw4sEprPmvj32KoTRWcJZN8ZU9JsF4In2Mqe-8k5JypY2Rzt5J719nSI082nJd81e1ktX1u6JYM4i5Bml0QvDJUyWPHzUiGhJMwnI4WLuSSKA-irrbuzhFfVCtvpm7VzTvxTrjEKBaCFOHBHCcJAsmiqBn0ecZY6TN9wbcvsDj3-1_uxJvh_KzXXnLg"
    sessionID = "sess_2PGpfTQVFevvno9K4PHQ1KYm3uB"
    text = "论文题目：基于Docker的HLS流媒体代理系统设计与实现，系统用到了RBAC模型管理，并且只针对HLS协议进行代理缓存，管理员可以查看操作日志和资源监控。根据以上特点，写出软件设计内容。"

    # email = Email() # Intialize a class
    # res = email.CreateAccount()
    # print(res)
    # client = res.client
    # sessionID = res.sessionID
    print(sessionID, client)

    forefront = Model(sessionID=sessionID, client=client, model="gpt-3.5-turbo")
    forefront.SetupConversation(text)
    for r in forefront.SendConversation():
        print(r.choices[0].delta.content, end='')


if __name__ == '__main__':
    main()
