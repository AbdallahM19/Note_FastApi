"""user_api.py"""

from fastapi import APIRouter, HTTPException, Query, Path, Request
from typing import Union, Optional, Annotated  #, List
from api.app import user_model
from api.database import UserDb
from api.models.users import UserAccount, convert_class_user_to_object
from api.utils.session import get_session, set_session, clear_session


router = APIRouter(
    prefix='/api',
)


@router.get("/users/{field}")
async def get_user(
    request: Request,
    field: Optional[str],
    user_id: Optional[int] = None,
    name: Optional[str] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
) -> Union[str, dict, list]:
    """
    Get user by id, or
    get all users with optional filtering and pagination.
    """
    users_data: Union[str, dict, list, None] = None
    # users_data = None

    match field:
        case "me":
            users_data = get_session(request)
        case "id" if user_id:
            users_data = user_model.get_user_by_id(user_id)
        case "name" if name:
            users_data = user_model.get_user_by_username(name, skip, limit)
        case "list":
            users_data = user_model.get_all_users_data(skip, limit)
        case _:
            users_data = f"Invalid field: '{field}'."

    if not users_data:
        raise HTTPException(status_code=404, detail="User not found")

    if isinstance(users_data, UserDb):
        return convert_class_user_to_object(users_data)

    if isinstance(users_data, list):
        if len(users_data) == 1:
            return convert_class_user_to_object(users_data[0])
        return [
            convert_class_user_to_object(i)
            for i in users_data
        ]

    return {"message": users_data}


@router.post("/users/register")
async def register(
    request: Request, username: Annotated[str, Query(min_length=3, max_length=50)],
    email: str, password: str, date_of_birth: Optional[str] = None,
    description: Annotated[Optional[str], Query(max_length=500)] = None
) -> dict:
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

        current_user = user_model.insert_new_user(
            username=username, email=email, hashed_password=password,
            date_of_birth=date_of_birth, description=description
        )

        set_session(request, **current_user)

        return {
            "message": "User created successfully", "user": current_user
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while registering the user: {str(e)}"
        ) from e


# @router.post("/users/login")
# async def login(username: str, password: str) -> dict:
#     """Login a user"""
#     try:
#         existed_user = user_model.authenticate_user(username, password)

#         if isinstance(existed_user, dict):
#             return {
#                 "status": 200,
#                 "message": "User logged in successfully",
#                 "user": existed_user
#             }
#         return {
#             "status": 401,
#             "message": existed_user,
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"An error occurred while logging the user: {str(e)}"
#         ) from e


@router.post("/users/login")
async def login(
    request: Request,
    password: str,
    username: Annotated[Optional[str], Query(min_length=3, max_length=50)] = None,
    email: Annotated[Optional[str], Query(
        max_length=100,
        pattern=r"^([a-z]+)((([a-z]+)|(_[a-z]+))?(([0-9]+)|(_[0-9]+))?)*@([a-z]+).([a-z]+)$"
    )] = None,
) -> dict:
    """Login a user and set session data."""
    try:
        existed_user = user_model.check_if_user_exists(username=username, email=email)

        if existed_user:
            if existed_user.hashed_password == password:
                current_user = convert_class_user_to_object(existed_user)

                set_session(request, **current_user)

                return {
                    "status": 200,
                    "message": "User logged in successfully",
                    "user": current_user
                }
            return {
                "status": 401,
                "message": "Invalid password. password not correct",
            }
        return {
            "status": 401,
            "message": "Invalid username. user not exists",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while logging the user: {str(e)}"
        ) from e


@router.put("/users/{user_id}/update")
async def update_user_data(
    user_id: Annotated[
        int, Path(
            title="The ID of the user to update.",
            description="The ID of the user to update.",
            gt=0
        )
    ],
    user_account: UserAccount
) -> dict:
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
async def delete_user_account_completely(
    user_id: Annotated[
        int, Path(
            title="The ID of the user to delete.",
            description="This will delete the user account completely.",
            gt=0
        )
    ]
) -> dict:
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
