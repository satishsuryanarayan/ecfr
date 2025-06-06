from marshmallow import Schema, fields, validates, post_load, ValidationError


class CreateUser:
    def __init__(self, username: str, password: str, email: str) -> None:
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f"{self.__class__.__name__}(username={self.username}, password={self.password}, email={self.email} )"


class CreateUserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)

    @validates("username")
    def validate_username(self, username: str, **kwargs: dict) -> None:
        if len(username.strip()) < 6:
            raise ValidationError("Username must be at least 6 characters long.", fields=["username"])

    @validates("password")
    def validate_password(self, password: str, **kwargs: dict) -> None:
        if len(password.strip()) < 12:
            raise ValidationError("Password must be at least 12 characters long.", fields=["password"])

    @post_load
    def make_createuser(self, data: dict, **kwargs: dict) -> CreateUser:
        return CreateUser(**data)
