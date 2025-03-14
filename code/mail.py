import json
import re

import aiohttp
import asyncio
import aiofiles
from typing import Dict, List


BASEURL = 'https://api.guerrillamail.com/ajax.php'


async def createNewEmail() -> Dict[str, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASEURL}?f=get_email_address') as response:
            response_json = await response.json()

    async with aiofiles.open("config.json", mode='r') as file:
        credentials = json.loads(await file.read())
        credentials['email'] = response_json['email_addr']
        credentials['sid_token'] = response_json['sid_token']

    async with aiofiles.open("config.json", mode='w') as file:
        await file.write(json.dumps(credentials, indent=4))

    return {
        'email': response_json['email_addr'],
        'sid_token': response_json['sid_token'],
        'alias': response_json['alias'],
        'email_timestamp': response_json['email_timestamp']
    }


async def getEmailList(sid_token: str) -> Dict[str, List[Dict[str, str]]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASEURL}?f=get_email_list&offset=0&sid_token={sid_token}') as response:
            response_json = json.loads(await response.text())

    return {
        'list': response_json['list']
    }


async def getLatestEmail(sid_token: str) -> Dict[str, str]:
    while True:
        await asyncio.sleep(15)
        emailList = await getEmailList(sid_token)
        print(emailList)
        emailListLength = len(emailList['list'])
        if emailListLength > 1:
            break

    mail_id = emailList['list'][0]["mail_id"]
    url = f"https://www.guerrillamail.com/ajax.php?f=fetch_email&email_id=mr_{mail_id}&sid_token={sid_token}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            emailData = json.loads(await response.text())
    return emailData


async def getPoeOTPCode(sid_token: str) -> str:
    emailData = await getLatestEmail(sid_token)

    otp_code = re.findall(r"(\d+)</div>", emailData['mail_body'])[0]
    print("OTP CODE: " + otp_code)
    return otp_code


async def main():
    async with aiofiles.open("config.json", mode='r') as file:
        credentials = json.loads(await file.read())
    sid_token = credentials['sid_token']
    print(sid_token)
    # print(await createNewEmail())
    # print(await getEmailList(sid_token))
    # print(await getLatestEmail(sid_token))
    print(await getPoeOTPCode(sid_token))


if __name__ == '__main__':
    asyncio.run(main())