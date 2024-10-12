"""app.py"""

from typing import Union
from fastapi import APIRouter
from api.models.users import User

router = APIRouter()
user_model = User()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/home")
async def home():
    return {"message": "Welcome in Home"}


# @router.get("/register")
# for get html register


# @router.get("/login")
# for get html login
