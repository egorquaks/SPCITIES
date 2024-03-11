import os
from dotenv import load_dotenv

from base64 import b64encode

import requests


def get_name(discord_id):
    load_dotenv()
    card_id = os.getenv("CARD_ID")
    card_token = os.getenv("CARD_TOKEN")

    headers = {
        'Authorization': f"Bearer {str(b64encode(str(f'{card_id}:{card_token}').encode('utf-8')), 'utf-8')}"
    }

    url = 'https://spworlds.ru/api/public/users/' + discord_id

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['username']
    else:
        print(f"Ошибка: {response.status_code}")
