import os
from dotenv import load_dotenv

from base64 import b64encode

from aiohttp import ClientSession

load_dotenv()
CARD_ID = os.getenv("CARD_ID")
CARD_TOKEN = os.getenv("CARD_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


async def get_name(discord_id):
    async with ClientSession() as session:
        headers = {
            'Authorization': f"Bearer {str(b64encode(str(f'{CARD_ID}:{CARD_TOKEN}').encode('utf-8')), 'utf-8')}"
        }

        url = 'https://spworlds.ru/api/public/users/' + discord_id

        response = await session.get(url, headers=headers)

        if response.status == 200:
            return (await response.json())['username']
        else:
            print(f"Ошибка: {response.status}")


async def refresh_token(refresh_token1):
    async with ClientSession() as session:
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token1
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        tokens = await session.post('https://discord.com/api/v8/oauth2/token', data=data, headers=headers)
        return await tokens.json()


async def get_user_data_from_token(access_token):
    async with ClientSession() as session:
        headers = {
            "Authorization": f'Bearer {access_token}'
        }
        user_data = await session.get('https://discordapp.com/api/users/@me', headers=headers)
        return await user_data.json()
