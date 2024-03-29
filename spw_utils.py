import os
import asyncio
from base64 import b64encode

import redis
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()

CARD_ID = os.getenv("CARD_ID")
CARD_TOKEN = os.getenv("CARD_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


async def _get_name(discord_id):
    async with ClientSession() as session:
        url = 'https://spworlds.ru/api/public/users/' + discord_id
        headers = {
            'Authorization': f"Bearer {str(b64encode(str(f'{CARD_ID}:{CARD_TOKEN}').encode('utf-8')), 'utf-8')}"
        }
        response = await session.get(url, headers=headers)

        if response.status == 200:
            user = (await response.json())['username']
            return user
        else:
            print(f"Ошибка: {response.status}")


def put_into_redis(discord_id, data):
    url = 'https://spworlds.ru/api/public/users/' + discord_id
    redis_client.setex(url, 60*60*12, data)


async def get_name(discord_id):
    async with ClientSession() as session:
        url = 'https://spworlds.ru/api/public/users/' + discord_id
        cached_data = redis_client.get(url)
        if cached_data:
            print("FROM THE CACHE")
            return cached_data.decode('utf-8')
        else:
            print("FROM THE API")
            data = await _get_name(discord_id)
            put_into_redis(discord_id, data)
            return data


async def main():
    for ii in range(10):
        name = await get_name("508668125680500739")
        print(f"{name} {ii}")
        name = await get_name("533929660556247040")
        print(f"{name} {ii}")


if __name__ == '__main__':
    for i in range(1000):
        print(asyncio.run(get_name("508668125680500739")))
        print(asyncio.run(get_name("533929660556247040")))
