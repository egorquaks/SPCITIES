import os

import uvicorn
from discord_oauth2 import DiscordAuth
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse

import utils

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")

discord_auth = DiscordAuth(CLIENT_ID, CLIENT_SECRET, CALLBACK_URL)

app = FastAPI()


@app.get('/')
def home():
    return {"message": "api"}


@app.get('/login', response_class=RedirectResponse)
def home():
    login_url = discord_auth.login()
    return login_url


@app.get('/callback')
def callback(code: str):
    tokens = discord_auth.get_tokens(code)
    return tokens


class RefreshToken(BaseModel):
    refresh_token: str


@app.post('/refresh_token')
def refresh_token(refresh_token: RefreshToken):
    token = discord_auth.refresh_token(refresh_token.refresh_token)
    return token


class AccessToken(BaseModel):
    access_token: str


@app.post('/user')
def user(access_token: AccessToken):
    user_data = discord_auth.get_user_data_from_token(access_token.access_token)
    return user_data


@app.get("/users/{user_id}")
async def read_item(user_id):
    return {"nick": utils.get_name(user_id)}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
