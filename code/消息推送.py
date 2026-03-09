import time
import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import httpx

# 设置环境变量
TOKEN_KEY_FILE_NAME = """-----BEGIN PRIVATE KEY-----

-----END PRIVATE KEY-----"""  # 填写key文件路径
DEVICE_TOKEN = ''  # 填写DeviceToken

# 固定变量
TEAM_ID = ''
AUTH_KEY_ID = ''
TOPIC = 'me.fin.bark'
APNS_HOST_NAME = 'api.push.apple.com'


def generate_jwt():
    jwt_issue_time = int(time.time())

    jwt_header = json.dumps({"alg": "ES256", "kid": AUTH_KEY_ID})
    jwt_claims = json.dumps({"iss": TEAM_ID, "iat": jwt_issue_time})

    jwt_header_b64 = base64.urlsafe_b64encode(jwt_header.encode()).rstrip(b'=').decode()
    jwt_claims_b64 = base64.urlsafe_b64encode(jwt_claims.encode()).rstrip(b'=').decode()

    jwt_header_claims = f"{jwt_header_b64}.{jwt_claims_b64}"

    private_key = load_pem_private_key(TOKEN_KEY_FILE_NAME.encode(), password=None)

    signature = private_key.sign(
        jwt_header_claims.encode(),
        ec.ECDSA(hashes.SHA256())
    )

    jwt_signed_header_claims_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

    return f"{jwt_header_b64}.{jwt_claims_b64}.{jwt_signed_header_claims_b64}"


def send_push_notification(authentication_token, message="test"):
    url = f"https://{APNS_HOST_NAME}/3/device/{DEVICE_TOKEN}"
    headers = {
        "user-agent": "curl/7.88.1",
        "accept": "*/*",
        "apns-topic": TOPIC,
        "apns-push-type": "alert",
        "authorization": f"bearer {authentication_token}",
        "content-type": "application/x-www-form-urlencoded",
    }
    payload = {
        "aps": {
            "mutable-content": 1,
            "alert": message
        }
    }
    # https://bark.day.app/#/apns?id=%e6%8e%a8%e9%80%81%e5%8f%82%e6%95%b0%e6%a0%bc%e5%bc%8f
    # https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/generating_a_remote_notification
    payload = {
        "aps": {
            "mutable-content": 1,
            "alert": {
                "title" : "title",
                "body": "body"
            },
            "category": "myNotificationCategory",
            "sound": "minuet.caf"
        },
        "icon": "https://day.app/assets/images/avatar.jpg"
    }
    with httpx.Client(http2=True) as client:
        response = client.post(url, headers=headers, json=payload)
        return response


if __name__ == "__main__":
    auth_token = generate_jwt()
    print("生成的认证Token:", auth_token)
    response = send_push_notification(auth_token, "你好啊")
    print("推送响应状态码:", response.status_code)
    print("推送响应内容:", response.headers)

