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

from database import add_user
from jwt_utils import gen_jwt, decode_jwt, is_authed
from utils import get_name

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
    redirect_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}&response_type=code&scope=identify"
    return RedirectResponse(url=redirect_url)


@app.get('/logout')
async def logout(response: Response):
    response.delete_cookie(key="Authorization")
    response.headers["Location"] = "/"
    response.status_code = 302
    return response


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
        add_user(user_uuid)
        token = await gen_jwt(user_uuid)
        response.set_cookie(key="Authorization", value=token, max_age=604800)
        response.headers["Location"] = "/"
        response.status_code = 302
    return response

# @app.post('/user')
# async def user(access_token: AccessToken):
#     user_data = await get_user_data_from_token(access_token.access_token)
#     return user_data


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def read_item(user_id, request: Request):
    is_authed_ = is_authed(request.cookies.get('Authorization'))
    if not is_authed_:
        return "динаху"
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
