from fastapi import APIRouter
from typing import List, Union
from api.models.users import User

router = APIRouter()
user_model = User()


@router.get("/users")
async def get_limit_user(
    skip: Union[int, None] = 0,
    limit: Union[int, None] = 5,
    name: Union[str, None] = None
) -> Union[str, dict, list]:
    if name:
        return user_model.get_user_by_username(name)
    return user_model.get_all_users_data(skip, skip + limit)


@router.get("/users/")
async def get_all_users() -> List[dict]:
    return user_model.get_all_users_data()


@router.get("/users/me")
async def get_current_user() -> dict:
    return {"user_id": "the current user"}


@router.get("/users/{user_id}")
async def get_user_by_id(user_id: int) -> dict:
    return user_model.get_user_by_id(user_id)


@router.post("/users/new")
async def create_new_user(
    username: str, email: str, password: str,
    date_of_birth: Union[str, None] = None,
    description: Union[str, None] = None
):
    if user_model.check_if_user_exists(username=username, email=email):
        return {"error": "User already exists"}

    data = user_model.insert_new_user(
        username=username, email=email, hashed_password=password,
        date_of_birth=date_of_birth, description=description
    )

    return data


@router.put("/users/{user_id}/update")
async def update_user_data(
    user_id: int, username: Union[str, None] = None,
    email: Union[str, None] = None, password: Union[str, None] = None,
    date_of_birth: Union[str, None] = None, description: Union[str, None] = None
):
    user_updated = user_model.update_user_account(
        id=user_id, username=username, email=email, hashed_password=password,
        date_of_birth=date_of_birth, description=description
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
    if user_model.delete_user(user_id):
        return {
            "message": "User account has been deleted successfully",
            "status": 200
        }
    return {
        "message": "User account could not be deleted",
        "status": 500
    }


# @router.get("/user-name/")
# async def get_user_by_name(
#     name: str
# ) -> Union[dict, str]:
#     return user.user_by_name(name)
