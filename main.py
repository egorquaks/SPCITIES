import os

import uvicorn
from discord_oauth2 import DiscordAuth
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from starlette.responses import RedirectResponse, Response
from aiohttp import ClientSession

import utils
from jwt_utils import get_db_user, is_authed, gen_jwt

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")

discord_auth = DiscordAuth(CLIENT_ID, CLIENT_SECRET, CALLBACK_URL)

app = FastAPI()

discord_oauth2 = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://discord.com/api/oauth2/authorize",
    tokenUrl="https://discord.com/api/oauth2/token",
)


@app.get('/')
async def home():
    return {"message": "api"}


@app.get('/login', response_class=RedirectResponse)
async def login():
    redirect_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}&response_type=code&scope=identify"
    return RedirectResponse(url=redirect_url)


@app.get('/api/auth/discord/redirect')
async def callback(code: str, response: Response):
    async with ClientSession() as session:
        token_payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": CALLBACK_URL,
            "scope": "identify"
        }
        token_response = await session.post(url="https://discord.com/api/oauth2/token", data=token_payload)
        token_data = await token_response.json()
        access_token = token_data.get("access_token")
        if access_token is None:
            raise HTTPException(status_code=400, detail="Failed to retrieve access token")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        user_response = await session.get("https://discord.com/api/users/@me", headers=headers)
        user_uuid = (await user_response.json())["id"]
        token = gen_jwt(user_uuid)
        response.set_cookie(key="Authorization", value=token)

    return get_db_user(uuid=str(user_uuid))  # {"jwt": token}


class AccessToken(BaseModel):
    access_token: str


@app.post('/user')
async def user(access_token: AccessToken):
    user_data = await utils.get_user_data_from_token(access_token.access_token)
    return user_data


@app.get("/users/{user_id}")
async def read_item(user_id, request: Request):
    name = await utils.get_name(user_id)
    if not is_authed(request.cookies.get('Authorization')):
        return "динаху"
    if name is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"nick": name}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
