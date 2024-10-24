"""user_api.py"""

from typing import Union
from fastapi import APIRouter, HTTPException
from api.models.users import UserAccount, convert_class_user_to_object
from api.app import user_model
from api.database import UserDb
# from typing import List

router = APIRouter(
    prefix='/api',
)


@router.get("/users/{field}")
async def get_user(
    field: str,
    user_id: Union[int, None] = None,
    skip: Union[int, None] = None,
    limit: Union[int, None] = None,
    name: Union[str, None] = None,
) -> Union[str, dict, list]:
    """
    Get user by id, or
    get all users with optional filtering and pagination.
    """
    users_data = None

    match field:
        case "me":
            return {
                "user_id": "the current user"
            }
        case "id":
            users_data = user_model.get_user_by_id(user_id)
        case "name":
            users_data = user_model.get_user_by_username(name, skip, limit)
        case "list":
            users_data = user_model.get_all_users_data(skip, limit)

    if isinstance(users_data, UserDb):
        return convert_class_user_to_object(users_data)

    if isinstance(users_data, list):
        return [
            convert_class_user_to_object(i)
            for i in users_data
        ]

    return "User not found"


@router.post("/users/register")
async def register(
    username: str, email: str, password: str,
    date_of_birth: Union[str, None] = None,
    description: Union[str, None] = None
):
    """Register a new user"""
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

        return {
            "message": "User created successfully", "user": user
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while registering the user: {str(e)}"
        ) from e


@router.post("/users/login")
async def login(username: str, password: str):
    """Login a user"""

    try:
        existed_user = user_model.authenticate_user(username, password)

        if existed_user:
            return {
                "message": "User logged in successfully",
                "user": convert_class_user_to_object(existed_user)
            }
        return {
            "status": 401,
            "message": "Invalid username or password"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while logging the user: {str(e)}"
        ) from e


@router.put("/users/{user_id}/update")
async def update_user_data(user_id: int, user_account: UserAccount):
    """Update user Account"""
    user_updated = user_model.update_user_account(
        id=user_id, username=user_account.username, email=user_account.email,
        hashed_password=user_account.password, date_of_birth=user_account.date_of_birth,
        description=user_account.description
    )

    return {
        "message": "User data updated successfully",
        "user_data": user_updated,
        "status": 200
    } if user_updated else {
        "error": "User data update failed",
        "status": 500
    }


@router.delete("/users/{user_id}/delete")
async def delete_user_account_completely(user_id: int) -> dict:
    """Delete user Account permanently"""
    if user_model.delete_user(user_id):
        return {
            "message": "User account has been deleted successfully",
            "status": 200
        }
    return {
        "message": "User account could not be deleted",
        "status": 500
    }
