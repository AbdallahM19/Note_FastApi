"""users.py"""

from typing import Union
from pydantic import BaseModel
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError
from api.database import UserDb, get_session


def convert_class_user_to_object(user: UserDb) -> dict:
    """Convert a UserDb object to a User dict"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "hashed_password": user.hashed_password,
        "session_id": user.session_id,
        "time_created": user.time_created,
        "last_opened": user.last_opened,
        "date_of_birth": user.date_of_birth,
        "description": user.description,
    }


class UserAccount(BaseModel):
    """User account model."""
    username: str = None
    email: str = None
    password: str = None
    date_of_birth: str = None
    description: str = None


class User():
    """User Class"""
    def __init__(self):
        self.sess = get_session()
        # self.users_data = [
        #     {"id": 1, "username": "Ali"},
        #     {"id": 2, "username": "John"},
        #     {"id": 3, "username": "Jane"},
        #     {"id": 4, "username": "Bob"},
        #     {"id": 5, "username": "Alice"},
        #     {"id": 6, "username": "Charlie"},
        #     {"id": 7, "username": "Diana"},
        #     {"id": 8, "username": "Eva"},
        #     {"id": 9, "username": "Frank"},
        #     {"id": 10, "username": "Gabriel"},
        #     {"id": 11, "username": "Hannah"},
        #     {"id": 12, "username": "Isaac"},
        #     {"id": 13, "username": "Julia"},
        #     {"id": 14, "username": "Kevin"},
        #     {"id": 15, "username": "Lily"}
        # ]

    def get_user_by_id(self, user_id):
        """Get user by id function"""
        try:
            user = self.sess.query(UserDb).filter(
                UserDb.id == user_id
            ).first()
            return user
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error getting user by id: {str(e)}") from e
        finally:
            self.sess.close()

    def get_user_by_username(
        self, name: str, skip: int = 0, limit: int = None
    ) -> Union[list, dict, str]:
        """Get user by username function"""
        try:
            users_data = self.sess.query(UserDb).filter(
                UserDb.username.like(f"%{name.lower()}%")
            ).offset(skip).limit(limit).all()

            if not users_data:
                return f"User with name {name} not found"

            return users_data
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error getting user by username: {e}") from e
        finally:
            self.sess.close()

    def get_all_users_data(
        self,
        skip: Union[int, None],
        limit: Union[int, None]
    ) -> list:
        """Get all users in list of dict"""
        users = self.sess.query(UserDb)

        if skip is not None and limit is not None:
            return users.offset(skip).limit(limit).all()

        return users.all()

    def check_if_user_exists(self, username: str, email: str):
        """Check if user exists in database"""
        try:
            user_existed = self.sess.query(UserDb).filter(
                or_(
                    UserDb.username == username,
                    UserDb.email == email
                )
            ).first()
            if user_existed:
                return user_existed
            return None
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error checking user existence: {str(e)}") from e
        finally:
            self.sess.close()

    def authenticate_user(self, username: str, password: str):
        """Authenticate user by username and password"""
        try:
            user = self.sess.query(UserDb).filter(
                and_(
                    or_(
                        UserDb.username == username,
                        UserDb.email == username
                    ),
                    UserDb.hashed_password == password
                )
            ).first()
            if user:
                return convert_class_user_to_object(user)
            return None
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error authenticating user: {e}") from e
        finally:
            self.sess.close()

    def insert_new_user(self, **kwargs: dict):
        """Insert new user into database"""
        try:
            new_user = UserDb(**kwargs)
            self.sess.add(new_user)
            self.sess.commit()
            return convert_class_user_to_object(new_user)
        except SQLAlchemyError as e:
            self.sess.rollback()
            raise SQLAlchemyError(f"Error inserting new user: {e}") from e
        finally:
            self.sess.close()

    def update_user_account(self, **kwargs):
        """Update user account information"""
        try:
            user = self.sess.query(UserDb).filter(
                UserDb.id == kwargs['id']
            ).first()
            if user:
                for key, value in kwargs.items():
                    if key != 'id' and value is not None:
                        setattr(user, key, value)
                self.sess.commit()
                return convert_class_user_to_object(user)
            return False
        except SQLAlchemyError as e:
            self.sess.rollback()
            raise SQLAlchemyError(f"Error updating user account: {e}") from e
        finally:
            self.sess.close()

    def delete_user(self, user_id: int) -> bool:
        """Delete user Account permanently from database"""
        try:
            user = self.sess.query(UserDb).filter(
                UserDb.id == user_id
            ).first()
            if user:
                self.sess.delete(user)
                self.sess.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.sess.rollback()
            raise SQLAlchemyError(f"Error deleting user with id ({user_id}): {e}") from e
        finally:
            self.sess.close()
