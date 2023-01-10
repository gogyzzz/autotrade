import os
import json
import requests
import pendulum


from constants import credentials_path, base_url


def get_secrets():
    with open(credentials_path) as f:
        secrets = json.load(f)
        app_key = secrets["app_key"]
        app_secret = secrets["app_secret"]
    return app_key, app_secret


def get_token(app_key, app_secret):
    now = pendulum.now("Asia/Seoul")
    now_date = now.format('YYYY-MM-DD')

    token_path = f'tmp/secrets/{now_date}/token'

    if os.path.exists(token_path) is True:
        with open(token_path) as f:
            return f.read()
    else:
        url = f"{base_url}/oauth2/tokenP"

        headers = {"content-type": "application/json"}
        data = {"grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret}

        res = requests.post(url,
                            headers=headers,
                            data=json.dumps(data))

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as f:
            f.write(res.json()["access_token"])

        return res.json()["access_token"]


app_key, app_secret = get_secrets()
token = get_token(app_key, app_secret)
