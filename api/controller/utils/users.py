from typing import cast

import bcrypt
from flask import current_app
from sqlalchemy import insert, select
from sqlalchemy.engine import Connection
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.expression import exists

from bank.db import get_connection
from bank.dtos.utils.createuser import CreateUser
from bank.dtos.utils.user import User
from bank.model.utils.users import Users


class UsersController:
    @classmethod
    def register_user(cls, create_user: CreateUser) -> User:
        current_app.logger.debug("Adding user...")
        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                user_exists: int = connection.execute(
                    select(
                        exists().where(cast(ColumnElement[bool], Users.c.username == create_user.username)))).scalar()
                if not user_exists:
                    hashed_password: bytes = bcrypt.hashpw(create_user.password.encode(), bcrypt.gensalt(rounds=6))
                    connection.execute(insert(Users).values(username=create_user.username, password=hashed_password,
                                                            email=create_user.email)).close()
                    user: User = User(username=create_user.username, password=hashed_password.decode(),
                                      email=create_user.email)
                    current_app.logger.debug("Registered user: %s", user)
                    return user
                else:
                    raise AssertionError(f"Username={create_user.username} already exists")
        except AssertionError as ae:
            current_app.logger.error("Assertion failure: %s", ae, exc_info=False)
            raise ae
        except Exception as e:
            current_app.logger.error("Unknown error while adding user: %s", e, exc_info=True)
            raise e

    @classmethod
    def validate_user(cls, username: str, password: str) -> bool:
        current_app.logger.debug("Validating user...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                user_exists: int = connection.execute(
                    select(exists().where(cast(ColumnElement[bool], Users.c.username == username)))).scalar()
                if user_exists:
                    pwd: bytes = connection.execute(
                        select(Users.c.password).where(
                            cast(ColumnElement[bool], Users.c.username == username))).scalar()
                    if bcrypt.checkpw(password.encode(), pwd):
                        current_app.logger.debug(f"Password verified for username={username}")
                        return True
                    else:
                        raise AssertionError(f"Password invalid for username={username}")
                else:
                    raise AssertionError(f"Username={username} does not exist")
        except AssertionError as ae:
            current_app.logger.error("Assertion failure: %s", ae, exc_info=False)
            return False
        except Exception as e:
            current_app.logger.error("Unknown error while validating user: %s", e, exc_info=True)
            return False
