# -*- coding: utf-8 -*-
# @Time    : 2023/3/30
# @Author  : Naihe
# @Email   : 239144498@qq.com
# @File    : auth.py
# @Software: PyCharm
import json
from requests import Session
from bs4 import BeautifulSoup


class PoeAuthException(Exception):
    pass


class PoeAuth:
    def __init__(self) -> None:
        self.session = Session()
        self.login_url = "https://poe.com/login"
        self.auth_api_url = "https://poe.com/api/gql_POST"
        self.session.headers = {
            "Host": "poe.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "TE": "trailers"
        }

    def __get_form_key(self) -> str:
        response = self.session.get(self.login_url)
        soup = BeautifulSoup(response.text, features="html.parser")

        try:
            next_data = soup.find("script", id="__NEXT_DATA__")
            next_data = json.loads(next_data.text)
            form_key = next_data.get("props").get("formkey")
        except Exception as e:
            raise PoeAuthException(f"Error while getting form key: {e}")
        return form_key

    def send_verification_code(self, email: str = None, phone: str = None, mode: str = "email") -> dict:
        form_key = self.__get_form_key()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
            'Accept': '/',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://poe.com/login',
            'Content-Type': 'application/json',
            'Origin': 'https://poe.com',
            'poe-formkey': form_key,
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        })
        if mode == "email":
            data = {
                "queryName": "MainSignupLoginSection_sendVerificationCodeMutation_Mutation",
                "variables": {"emailAddress": email, "phoneNumber": None},
                "query": "mutation MainSignupLoginSection_sendVerificationCodeMutation_Mutation(\n $emailAddress: String\n $phoneNumber: String\n) {\n sendVerificationCode(verificationReason: login, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n status\n errorMessage\n }\n}\n"
            }
        elif mode == "phone":
            data = {
                "queryName": "MainSignupLoginSection_sendVerificationCodeMutation_Mutation",
                "variables": {"emailAddress": None, "phoneNumber": phone},
                "query": "mutation MainSignupLoginSection_sendVerificationCodeMutation_Mutation(\n $emailAddress: String\n $phoneNumber: String\n) {\n sendVerificationCode(verificationReason: login, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n status\n errorMessage\n }\n}\n"
            }
        else:
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        response = self.session.post(self.auth_api_url, json=data).json()

        if response.get("data") is not None:
            if response.get("data").get("sendVerificationCode").get("errorMessage") is not None:
                raise PoeAuthException(
                    f"Error while sending verification code: {response.get('data').get('sendVerificationCode').get('errorMessage')}")
            return response
        raise PoeAuthException(
            f"Error while sending verification code: {response}")

    def login_using_verification_code(self, verification_code: str, mode: str, email: str = None,
                                      phone: str = None) -> str:
        if mode == "email":
            data = {
                "queryName": "SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation",
                "variables": {"verificationCode": verification_code, "emailAddress": email, "phoneNumber": None},
                "query": "mutation SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation(\n  $verificationCode: String!\n  $emailAddress: String\n  $phoneNumber: String\n) {\n  loginWithVerificationCode(verificationCode: $verificationCode, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n    status\n    errorMessage\n  }\n}\n"
            }
        elif mode == "phone":
            data = {
                "queryName": "SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation",
                "variables": {"verificationCode": verification_code, "emailAddress": None, "phoneNumber": phone},
                "query": "mutation SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation(\n  $verificationCode: String!\n  $emailAddress: String\n  $phoneNumber: String\n) {\n  loginWithVerificationCode(verificationCode: $verificationCode, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n    status\n    errorMessage\n  }\n}\n"
            }
        else:
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        response = self.session.post(self.auth_api_url, json=data).json()
        if response.get("data") is not None:
            if response.get("data").get("loginWithVerificationCode").get("errorMessage") is not None:
                raise PoeAuthException(
                    f"Error while login in using verification code: {response.get('data').get('loginWithVerificationCode').get('errorMessage')}")
            return self.session.cookies.get_dict().get("p-b")
        raise PoeAuthException(
            f"Error while login in using verification code: {response}")


from requests import Session
from string import ascii_letters
from random import choices


class Mail:
    def __init__(self, proxies: dict = None) -> None:
        self.client = Session()
        self.client.proxies = None  # proxies
        self.client.headers = {
            "host": "api.mail.tm",
            "connection": "keep-alive",
            "sec-ch-ua": "\"Google Chrome\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"macOS\"",
            "origin": "https://mail.tm",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mail.tm/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8"
        }

    def get_mail(self, user=None) -> str:
        token = user or ''.join(choices(ascii_letters, k=10)).lower()

        init = self.client.post("https://api.mail.tm/accounts", json={
            "address": f"{token}@bugfoo.com",
            "password": token
        })

        if init.status_code == 201:
            resp = self.client.post("https://api.mail.tm/token", json={
                **init.json(),
                "password": token
            })

            self.client.headers['authorization'] = 'Bearer ' + resp.json()['token']

            return f"{token}@bugfoo.com"

        else:
            raise Exception("Failed to create email")

    def fetch_inbox(self):
        return self.client.get(f"https://api.mail.tm/messages").json()["hydra:member"]

    def get_message(self, message_id: str):
        return self.client.get(f"https://api.mail.tm/messages/{message_id}").json()

    def get_message_content(self, message_id: str):
        return self.get_message(message_id)["text"]


def main():
    email = input("Enter email address or phone number: ")

    poeauth = PoeAuth()

    if email is None:
        print("Email address or phone number is required.")
        return

    try:
        if email:
            resp = poeauth.send_verification_code(email=email)
    except PoeAuthException as e:
        print(str(e))
        return

    verification_code = input(
        f"Enter the verification code sent to {email}: ")

    try:
        if email:
            auth_session = poeauth.login_using_verification_code(
                verification_code=verification_code, mode="email", email=email)
        else:
            auth_session = None
    except PoeAuthException as e:
        print(str(e))
        return

    print(f"Successful authentication. Session cookie: {auth_session}")


if __name__ == '__main__':
    # main()
    client = Mail()
    client.get_mail()