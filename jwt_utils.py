import os

from dotenv import load_dotenv
from jose import jwt, JWTError
from pydantic import BaseModel

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


def gen_jwt(uuid):
    return jwt.encode({'key': uuid}, SECRET, algorithm='HS256')


def decode_jwt(token):
    return jwt.decode(token, SECRET, algorithms=['HS256'])


def is_authed(jwt_token: str):
    if jwt_token is None:
        return False
    try:
        uuid = decode_jwt(jwt_token)["key"]
    except JWTError:
        return False
    if uuid in fake_users_db:
        return True
    return False
