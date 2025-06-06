from marshmallow import Schema, fields, post_load


class User:
    def __init__(self, username: str, password: str, email: str) -> None:
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f"{self.__class__.__name__}(username={self.username}, password={self.password}, email={self.email})"


class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)

    @post_load
    def make_user(self, data: dict, **kwargs: dict) -> User:
        return User(**data)
