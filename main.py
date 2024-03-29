import asyncio
import os

import uvicorn
from discord_oauth2 import DiscordAuth
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from starlette.responses import RedirectResponse, Response, HTMLResponse
from aiohttp import ClientSession
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import database
from jwt_utils import gen_jwt, decode_jwt, is_authed
from spw_utils import get_name
from utils import get_user_from_token, get_code_data

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")

discord_auth = DiscordAuth(CLIENT_ID, CLIENT_SECRET, CALLBACK_URL)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

discord_oauth2 = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://discord.com/api/oauth2/authorize",
    tokenUrl="https://discord.com/api/oauth2/token",
)


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    is_authed_ = is_authed(request.cookies.get('Authorization'))
    if is_authed_:
        name = decode_jwt(request.cookies.get('Authorization'))['name']
        uuid = decode_jwt(request.cookies.get('Authorization'))['uuid']
        return templates.TemplateResponse(
            request=request, name="index.html", context={"is_authed": is_authed_, "name": name, "uuid": uuid}
        )
    else:
        return templates.TemplateResponse(
            request=request, name="index.html", context={"is_authed": is_authed_}
        )


@app.get('/login', response_class=RedirectResponse)
async def login():
    redirect_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}&response_type=code&scope=identify%20guilds.members.read"
    return RedirectResponse(url=redirect_url)


@app.get('/api/auth/discord/redirect')
async def callback(code: str, response: Response):
    async with ClientSession() as session:
        token_response = await get_code_data(code)
        print(await token_response.json())
        token_data = await token_response.json()
        access_token = token_data.get("access_token")
        if access_token is None:
            raise HTTPException(status_code=400, detail="Failed to retrieve access token")
        user_info = await get_user_from_token(access_token)
        print(await user_info.json())
        user_uuid = (await user_info.json())["id"]
        await database.add_user(user_uuid)
        token = await gen_jwt(user_uuid)
        response.set_cookie(key="Authorization", value=token, max_age=604800)
        response.headers["Location"] = "/"
        response.status_code = 302
    return response


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def read_item(user_id, request: Request):
    is_authed_ = is_authed(request.cookies.get('Authorization'))
    if not is_authed_:
        return templates.TemplateResponse(name="forbidden.html",request=request)
    name = await get_name(user_id)
    if name is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    client_uuid = decode_jwt(request.cookies.get('Authorization'))['uuid']
    client_name = decode_jwt(request.cookies.get('Authorization'))['name']
    return templates.TemplateResponse(
        request=request, name="user_profile.html",
        context={"is_authed": is_authed_, "name": name, "client_name": client_name, "client_uuid": client_uuid}
    )

if __name__ == '__main__':
    asyncio.run(database.init())
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
