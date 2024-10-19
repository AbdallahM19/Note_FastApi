"""app.py"""

# from typing import Union
from fastapi import APIRouter
from api.models.users import User
from api.models.notes import Note


router = APIRouter()
user_model = User()
note_model = Note()


@router.get("/")
async def root():
    """root"""
    return {"message": "Hello World"}


@router.get("/home")
async def home():
    """Home Page"""
    return {"message": "Welcome in Home"}


# @router.get("/register")
# for get html register


# @router.get("/login")
# for get html login
