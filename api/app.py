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


@router.post("/register")
async def register(
    username: str, email: str, password: str,
    date_of_birth: Union[str, None] = None,
    description: Union[str, None] = None
):
    try:
        existing_user = user_model.check_if_user_exists(username, email)
        if existing_user:
            return {
                "message": "User already exists. Please try with different username or email."
                if existing_user.username == username else
                "User already exists. Please try with different email.",
                "status": 400
            }

        user = user_model.insert_new_user(
            username=username, email=email, hashed_password=password,
            date_of_birth=date_of_birth, description=description
        )

        return {"message": "User created successfully", "user": user}
    except Exception as e:
        return {"message": str(e), "status": 500}


# @router.get("/login")
# for get html login


@router.post("/login")
async def login(username: str, password: str):
    try:
        existed_user = user_model.authenticate_user(username, password)

        if existed_user:
            return {"message": "User logged in successfully", "user": existed_user}
        return {"message": "Invalid username or password", "status": 401,}
    except Exception as e:
        return {"message": str(e), "status": 500}
