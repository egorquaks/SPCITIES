import os
from dotenv import load_dotenv

from base64 import b64encode

import requests


def get_name(discord_id):
    load_dotenv()
    # Замените 'ID' и 'TOKEN' на реальные значения
    card_id = os.getenv("CARD_ID")
    card_token = os.getenv("CARD_TOKEN")

    # Формируем заголовок Authorization
    headers = {
        'Authorization': f"Bearer {str(b64encode(str(f'{card_id}:{card_token}').encode('utf-8')), 'utf-8')}"
    }

    # URL для запроса
    url = 'https://spworlds.ru/api/public/users/' + discord_id

    # Отправляем GET-запрос
    response = requests.get(url, headers=headers)

    # Проверяем статус код
    if response.status_code == 200:
        # Обрабатываем ответ (например, выводим содержимое)
        print(response.json()['username'])
    else:
        print(f"Ошибка: {response.status_code}")
