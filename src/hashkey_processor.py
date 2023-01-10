import json
import requests

from secrets import app_key, app_secret
from constants import base_url


class HashKeyProcessor:
    def __init__(self):
        pass

    def to_hash(self, data):
        url = f"{base_url}/uapi/hashkey"

        headers = {
            "content-type": "application/json",
            "appKey": app_key,
            "appSecret": app_secret
        }

        res = requests.post(url, headers=headers, data=json.dumps(data))

        return res.json()["HASH"]
