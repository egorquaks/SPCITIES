import os

from dotenv import load_dotenv
from jose import jwt, JWTError
from pydantic import BaseModel

from spw_utils import get_name

UUID = "304890931008503808"
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

fake_users_db = {
    "304890931008503808": {
        "access": True
    }
}


class User(BaseModel):
    access: bool


def get_db_user(uuid: str):
    if uuid in fake_users_db:
        user_dict = fake_users_db[uuid]
        print(user_dict)
        return User(**user_dict)


async def gen_jwt(uuid):
    name = await get_name(uuid)
    return jwt.encode({'uuid': uuid, 'name': name}, JWT_SECRET, algorithm='HS256')


def decode_jwt(token):
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])


def is_authed(jwt_token: str):
    if jwt_token is None:
        return False
    try:
        uuid = decode_jwt(jwt_token)["uuid"]
    except JWTError:
        return False
    if uuid in fake_users_db:
        return True
    return False
