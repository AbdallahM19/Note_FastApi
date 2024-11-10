"""user_api.py"""

from typing import Union, Optional, Annotated  #, List
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from api.app import user_model
from api.database import UserDb
from api.models.users import UserAccount, convert_class_user_to_object
from api.utils.session import SessionManager, get_session_manager


router = APIRouter(
    prefix='/api',
    tags=['user-api']
)


@router.get("/users/{field}")
async def get_user(
    field: Optional[str],
    user_id: Optional[int] = None,
    name: Optional[str] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    session: SessionManager = Depends(get_session_manager)
) -> Union[str, dict, list]:
    """
    Get user by id, or
    get all users with optional filtering and pagination.
    """
    users_data: Union[str, dict, list, None] = None
    # users_data = None

    match field:
        case "me":
            users_data = user_model.get_user_by_session_id(session.get_session_id())
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
    username: Annotated[str, Query(min_length=3, max_length=50)],
    email: str, password: str, date_of_birth: Optional[str] = None,
    description: Annotated[Optional[str], Query(max_length=500)] = None,
    session: SessionManager = Depends(get_session_manager)
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

        session_id = str(uuid4())

        current_user = user_model.insert_new_user(
            username=username, email=email, hashed_password=password,
            date_of_birth=date_of_birth, description=description,
            session_id=session_id
        )

        session.set_session_id(session_id)

        return {"message": "User created successfully", "user": current_user}
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
    password: str,
    username: Annotated[Optional[str], Query(min_length=3, max_length=50)] = None,
    email: Annotated[Optional[str], Query(
        max_length=100,
        pattern=r"^([a-z]+)((([a-z]+)|(_[a-z]+))?(([0-9]+)|(_[0-9]+))?)*@([a-z]+).([a-z]+)$"
    )] = None,
    session: SessionManager = Depends(get_session_manager)
) -> dict:
    """Login a user and set session data."""
    try:
        existed_user = user_model.check_if_user_exists(username=username, email=email)

        if existed_user:
            if existed_user.hashed_password == password:
                current_user = convert_class_user_to_object(existed_user)

                session.set_session_id(current_user["session_id"])

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
        Union[int, str], Path(
            title= "Update user by id or 'me'",
            description= "Update user data by id or 'me' to update current user data",
            gt=0
        )
    ],
    user_account: UserAccount,
    session: SessionManager = Depends(get_session_manager)
) -> dict:
    """Update user Account"""
    try:
        user_updated = None

        if isinstance(user_id, str) and user_id == 'me':
            user_updated = user_model.update_user_account(
                session_id=session.get_session_id(), **user_account
            )
        if isinstance(user_id, int):
            user_updated = user_model.update_user_account(
                id=user_id, **user_account
            )

        if user_updated:
            return {
                "message": "User data updated successfully",
                "user_data": user_updated,
                "status": 200
            }
        return {
            "error": "User data update failed",
            "search": user_id,
            "status": 400,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred while updating the user: {str(e)}"
        ) from e


@router.delete("/users/{user_id}/delete")
async def delete_user_account_completely(
    user_id: Annotated[
        int, Path(
            title="The ID of the user to delete.",
            description="This will delete the user account completely.",
            gt=0
        )
    ],
    session: SessionManager = Depends(get_session_manager)
) -> dict:
    """Delete user Account permanently"""
    if user_model.delete_user(user_id):
        session.clear_session()

        return {
            "message": "User account has been deleted successfully",
            "status": 200
        }
    return {
        "message": "User account could not be deleted",
        "status": 500
    }

@router.delete("/users/logout")
async def logout_user(session: SessionManager = Depends(get_session_manager)) -> dict:
    """Logout user"""
    session.clear_session()
    return {"message": "User logged out successfully", "status": 200}
