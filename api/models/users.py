from sqlalchemy import or_, and_
from api.database import User_db, get_session
from pydantic import BaseModel
from typing import Union


class CurrentUser(BaseModel):
    """Model for the current user."""
    id: int
    username: str


class User():
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
        user = self.sess.query(User_db).filter(
            User_db.id == user_id
        ).first()
        return self.convert_class_user_to_object(user)

    def get_user_by_username(
        self, name: str, skip: int = None, limit: int = None
    ) -> Union[list, dict, str]:
        try:
            if skip is None and type(limit) is int:
                skip = 0

            users_data = self.sess.query(User_db).filter(
                User_db.username.like("%{}%".format(name.lower()))
            ).offset(skip).limit(limit).all()

            if not users_data:
                return "User with name {} not found".format(name)

            if len(users_data) == 1:
                return self.convert_class_user_to_object(users_data[0])
            else:
                return [
                    self.convert_class_user_to_object(i)
                    for i in users_data
                ]
        except Exception as e:
            print("Error in get_user_by_username: {}".format(e))
            raise

    def get_all_users_data(
        self,
        skip: Union[int, None],
        limit: Union[int, None]
    ) -> list:
        if skip is not None and limit is not None:
            users = self.sess.query(User_db).offset(skip).limit(limit).all()
            return [
                self.convert_class_user_to_object(i)
                for i in users
            ]
        return [
            self.convert_class_user_to_object(i)
            for i in self.sess.query(User_db).all()
        ]

    def check_if_user_exists(self, username: str, email: str):
        user_existed = self.sess.query(User_db).filter(
            or_(
                User_db.username == username,
                User_db.email == email
            )
        ).first()
        if user_existed:
            return user_existed
        return False

    def authenticate_user(self, username: str, password: str):
        user = self.sess.query(User_db).filter(
            and_(
                or_(
                    User_db.username == username,
                    User_db.email == username
                ),
                User_db.hashed_password == password
            )
        ).first()
        return self.convert_class_user_to_object(user)

    def insert_new_user(self, **kwargs: dict):
        try:
            new_user = User_db(**kwargs)
            self.sess.add(new_user)
            self.sess.commit()
            return self.convert_class_user_to_object(new_user)
        except Exception as e:
            self.sess.rollback()
            print("Error inserting new user: {}".format(e))
            return False
        finally:
            self.sess.close()

    def update_user_account(self, **kwargs):
        try:
            user = self.sess.query(User_db).filter(
                User_db.id == kwargs['id']
            ).first()
            if user:
                for key, value in kwargs.items():
                    if key != 'id' and value is not None:
                        setattr(user, key, value)
                self.sess.commit()
                return self.convert_class_user_to_object(user)
            return False
        except Exception as e:
            self.sess.rollback()
            print("Error updating user account: {}".format(e))
            return False
        finally:
            self.sess.close()

    def delete_user(self, user_id: int) -> bool:
        try:
            user = self.sess.query(User_db).filter(
                User_db.id == user_id
            ).first()
            if user:
                self.sess.delete(user)
                self.sess.commit()
                return True
            return False
        except Exception as e:
            self.sess.rollback()
            print("Error deleting user with id {}: {}".format(user_id, e))
        finally:
            self.sess.close()
                

    def convert_class_user_to_object(self, user) -> dict:
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